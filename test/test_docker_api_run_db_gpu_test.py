import unittest

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.models.accelerator import Accelerator


class ApiDockerRunDbTestWithGPU(unittest.TestCase):
    #
    # Spawn a Docker db and run gpu tests.
    #
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def _run_db_test(self, accelerator: Accelerator, test_file: str):
        result = api.run_db_test(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            test_container_folder=str(exaslct_utils.get_full_test_container_folder()),
            output_directory=self.test_environment.output_dir,
            accelerator=accelerator,
            test_file=(test_file,),
        )
        assert result.tests_are_ok

    def test_run_gpu_enabled_test(self):
        self._run_db_test(Accelerator.NVIDA, "test_gpu_enabled.py")

    def test_run_gpu_disabled_test(self):
        self._run_db_test(Accelerator.NONE, "test_gpu_disabled.py")


if __name__ == "__main__":
    unittest.main()
