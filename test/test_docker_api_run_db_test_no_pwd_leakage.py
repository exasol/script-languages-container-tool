import os
import unittest

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api


class ApiDockerRunDbTestNoPasswordLeakage(unittest.TestCase):
    """
    Spawn a Docker db and run test and validate that Docker password was not written to build output directory.
    """

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    @unittest.skipIf(
        os.getenv("DOCKER_USER") is None or os.getenv("DOCKER_PASSWD") is None,
        "Docker credentials not configured",
    )
    def test_run_db_test_no_leakage(self):
        docker_user = os.getenv("DOCKER_USER")
        docker_password = os.getenv("DOCKER_PASSWD")
        _ = api.run_db_test(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            test_container_folder=str(exaslct_utils.get_full_test_container_folder()),
            output_directory=self.test_environment.output_dir,
            source_docker_username=docker_user,
            source_docker_password=docker_password,
            test_file=("empty_test.py",),
        )
        for folder, dirs, files in os.walk(self.test_environment.output_dir):
            for file in files:
                if not file.endswith(".tar.gz"):
                    fullpath = os.path.join(folder, file)
                    print(f"Testing {fullpath}")
                    with open(fullpath) as f:
                        for line in f:
                            self.assertFalse(
                                docker_password not in line,
                                f"Found docker password in file {fullpath}",
                            )


if __name__ == "__main__":
    unittest.main()
