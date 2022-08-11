import unittest

from exasol_integration_test_docker_environment.lib.docker.container.utils import remove_docker_container

import utils as exaslct_utils


class DockerRunDBTestDockerDBTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()

    def tearDown(self):
        self.remove_docker_container()
        self.test_environment.close()

    def remove_docker_container(self):
        remove_docker_container([f"test_container_{self.test_environment.name}",
                                       f"db_container_{self.test_environment.name}"])

    def test_run_db_tests_docker_db(self):
        command = f"{self.test_environment.executable} run-db-test "
        self.test_environment.run_command(
            command, track_task_dependencies=True)


if __name__ == '__main__':
    unittest.main()
