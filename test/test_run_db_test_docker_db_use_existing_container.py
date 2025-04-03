import shutil
import unittest
from pathlib import Path

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.docker import ContextDockerClient
from exasol_integration_test_docker_environment.lib.docker.container.utils import (
    remove_docker_container,
)

from exasol.slc.internal.utils.docker_utils import find_images_by_tag


class DockerRunDBTestDockerUseExistingContainer(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.test_environment.clean_images()
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

    def _has_docker_images_for_test_flavor(self) -> bool:
        with ContextDockerClient() as docker_client:
            images = find_images_by_tag(
                docker_client,
                lambda tag: tag.startswith(
                    f"{self.test_environment.repository_name}:test-flavor"
                ),
            )
            return len(images) > 0

    @property
    def _get_container_file(self):
        exported_container_file_glob = list(
            self.tmp_container_file_dir.glob("**/*.tar.gz")
        )
        self.assertEqual(len(exported_container_file_glob), 1)
        return str(exported_container_file_glob[0])

    @property
    def _cache_dir(self):
        return Path(self.test_environment.temp_dir) / "cache"

    def _clean_up_container(self):
        self.assertTrue(self._has_docker_images_for_test_flavor())
        self.test_environment.clean_images()
        self.assertFalse(self._has_docker_images_for_test_flavor())
        cache_glob = list(self._cache_dir.glob("**/*.tar.gz"))
        self.assertEqual(len(cache_glob), 1)
        shutil.rmtree(self._cache_dir)

    def _run_export(self):
        command = [
            self.test_environment.executable,
            "export",
            "--export-path",
            str(self.tmp_container_file_dir),
        ]
        self.test_environment.run_command(" ".join(command))

    def _run_db_test_with_use_existing_container(self):
        command = [
            self.test_environment.executable,
            "run-db-test",
            exaslct_utils.get_full_test_container_folder_parameter(),
            "--use-existing-container",
            self._get_container_file,
        ]
        self.test_environment.run_command(
            " ".join(command), track_task_dependencies=True
        )

    def test_run_db_tests_docker_db_use_existing_container(self):
        self._run_export()
        self._clean_up_container()
        self._run_db_test_with_use_existing_container()

        # Verify that the docker container and cache was not re-created
        self.assertTrue(self._cache_dir.exists())
        cache_glob = list(self._cache_dir.glob("**/*.tar.gz"))
        self.assertEqual(len(cache_glob), 0)
        self.assertFalse(self._has_docker_images_for_test_flavor())


if __name__ == "__main__":
    unittest.main()
