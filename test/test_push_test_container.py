import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing.docker_registry import (
    LocalDockerRegistryContextManager,
)


class PushTestContainerTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.test_environment.clean_images()

    def tearDown(self):
        self.test_environment.close()

    def test_push_test_container(self):
        with LocalDockerRegistryContextManager(
            self.test_environment.name
        ) as local_registry:
            self.test_environment.repository_name = local_registry.name
            parameter = exaslct_utils.get_mock_test_container_folder_parameter()
            command = (
                f"{self.test_environment.executable} push-test-container {parameter}"
            )
            self.test_environment.run_command(
                command, track_task_dependencies=True, use_flavor_path=False
            )
            images = local_registry.images
            self.assertRegex(images["tags"][0], "db-test-container_.*")


if __name__ == "__main__":
    unittest.main()
