import shutil
import unittest
from pathlib import Path

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.docker import ContextDockerClient
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.internal.utils.docker_utils import find_images_by_tag


class ApiDockerRunDbTestUseExistingContainer(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    @property
    def _cache_dir(self):
        return Path(self.test_environment.output_dir) / "cache"

    def _has_docker_images_for_test_flavor(self) -> bool:
        with ContextDockerClient() as docker_client:
            images = find_images_by_tag(
                docker_client,
                lambda tag: tag.startswith(
                    f"{self.test_environment.docker_repository_name}:test-flavor"
                ),
            )
            return len(images) > 0

    def _clean_up_container(self):
        self.assertTrue(self._has_docker_images_for_test_flavor())
        self.test_environment.clean_all_images()
        self.assertFalse(self._has_docker_images_for_test_flavor())
        cache_glob = list(self._cache_dir.glob("**/*.tar.gz"))
        self.assertEqual(len(cache_glob), 1)
        shutil.rmtree(self._cache_dir)

    def _run_export(self) -> str:
        export_result = api.export(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            export_path=self.export_path,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            output_directory=self.test_environment.output_dir,
        )
        self.assertEqual(len(export_result.export_infos), 1)
        export_infos_for_flavor = export_result.export_infos[
            str(exaslct_utils.get_test_flavor())
        ]
        self.assertEqual(len(export_infos_for_flavor), 1)
        export_info = export_infos_for_flavor["release"]
        self.assertIsNotNone(export_info.output_file)

        export_path = Path(export_info.output_file)
        self.assertTrue(export_path.exists())
        return str(export_path)

    def _run_db_test(self, container_file: str):
        api.run_db_test(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            use_existing_container=container_file,
            test_container_folder=str(exaslct_utils.get_full_test_container_folder()),
            output_directory=self.test_environment.output_dir,
        )

    def test_run_db_test_use_existing_container(self):
        container_file = self._run_export()
        self._clean_up_container()
        self._run_db_test(container_file)

        # Verify that the docker container and cache was not re-created
        self.assertTrue(self._cache_dir.exists())
        cache_glob = list(self._cache_dir.glob("**/*.tar.gz"))
        self.assertEqual(len(cache_glob), 0)
        self.assertFalse(self._has_docker_images_for_test_flavor())


if __name__ == "__main__":
    unittest.main()
