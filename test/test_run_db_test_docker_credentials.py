import os
import unittest

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore


class RunDBTestDockerCredentials(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.test_environment.clean_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    @unittest.skipIf(
        os.getenv("DOCKER_USER") is None or os.getenv("DOCKER_PASSWD") is None,
        "Docker credentials not configured",
    )
    def test_docker_credentials_injection_into_test_container(self):
        docker_user = os.getenv("DOCKER_USER")
        docker_password = os.getenv("DOCKER_PASSWD")
        arguments = " ".join(
            [
                f"--source-docker-username={docker_user}",
                f"--source-docker-password={docker_password}",
                exaslct_utils.get_full_test_container_folder_parameter(),
            ]
        )

        command = (
            f"{self.test_environment.executable} run-db-test {arguments} "
            f"--test-file test_container_docker_credentials.py"
        )
        self.test_environment.run_command(command, track_task_dependencies=True)


if __name__ == "__main__":
    unittest.main()
