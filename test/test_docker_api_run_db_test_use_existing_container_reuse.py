import unittest
from pathlib import Path
from typing import Dict

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api


class ApiDockerRunDbTestUseExistingContainerReuse(unittest.TestCase):
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()
        self._test_container_name = (
            f"test_container_{exaslct_utils.get_test_flavor().name}_release"
        )
        self._db_container_name = (
            f"db_container_{exaslct_utils.get_test_flavor().name}_release"
        )

    def tearDown(self):
        utils.close_environments(self.test_environment)

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
            reuse_test_environment=True,
            output_directory=self.test_environment.output_dir,
        )

    def test_run_db_test_use_existing_container_reuse(self):
        def container_ids() -> dict[str, str]:
            return exaslct_utils.get_docker_container_ids(
                self._test_container_name,
                self._db_container_name,
            )

        container_file = self._run_export()
        self._run_db_test(container_file)
        old_ids = container_ids()
        self._run_db_test(container_file)
        new_ids = container_ids()
        self.assertEqual(old_ids, new_ids)


if __name__ == "__main__":
    unittest.main()
