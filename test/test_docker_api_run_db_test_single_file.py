import subprocess
import tarfile
import unittest
from tempfile import TemporaryDirectory

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.data.environment_type import (
    EnvironmentType,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.models.compression_strategy import CompressionStrategy


class ApiDockerRunDbTestSingleFile(unittest.TestCase):
    #
    # Spawn a Docker db and run test for single file.
    #
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_run_db_test_single_file(self):
        result = api.run_db_test(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            test_container_folder=str(exaslct_utils.get_full_test_container_folder()),
            output_directory=self.test_environment.output_dir,
            test_file=("empty_test.py",),
        )
        flavor_keys = list(result.test_results_per_flavor.keys())
        self.assertEqual(len(flavor_keys), 1)
        flavor_key = flavor_keys[0]

        test_result_per_flavor = result.test_results_per_flavor[flavor_key]
        test_result_per_release = test_result_per_flavor.test_results_per_release_goal[
            "release"
        ]
        test_file_output = test_result_per_release.test_files_output
        self.assertEqual(len(test_file_output.test_results), 1)
        test_results = test_file_output.test_results[0]
        self.assertEqual(len(test_results.test_results), 1)
        test_result = test_results.test_results[0]
        self.assertEqual(test_result.test_file, "empty_test.py")
        self.assertEqual(test_result.language, "None")
        self.assertTrue(test_result.is_ok)


if __name__ == "__main__":
    unittest.main()
