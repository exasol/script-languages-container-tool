import unittest

import docker

from exasol_script_languages_container_tool.lib.utils.docker_utils import find_images_by_tag

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class BuildTestContainerTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.docker_client = docker.from_env()
        self.test_environment.clean_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)
        utils.close_environments(self.test_environment)

    def test_build_test_container(self):
        parameter = exaslct_utils.get_mock_test_container_folder_parameter()
        command = f"{self.test_environment.executable} build-test-container {parameter}"
        self.test_environment.run_command(command, track_task_dependencies=True, use_flavor_path=False)
        images = find_images_by_tag(self.docker_client,
                                    lambda tag: tag.startswith(self.test_environment.repository_name))
        self.assertTrue(len(images) > 0,
                        f"Did not found images for repository "
                        f"{self.test_environment.repository_name} in list {images}")


if __name__ == '__main__':
    unittest.main()
