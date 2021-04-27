import unittest

import docker
from exasol_integration_test_docker_environment.test import utils

from exasol_script_languages_container_tool.lib.utils.docker_utils import find_images_by_tag

import utils as exaslct_utils


class DockerBuildTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = utils.ExaslctTestEnvironment(self,exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.docker_client = docker.from_env()
        self.test_environment.clean_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)
        try:
            self.test_environment.close()
        except Exception as e:
            print(e)

    def test_docker_build(self):
        command = f"{self.test_environment.executable} build"
        self.test_environment.run_command(command, track_task_dependencies=True)
        images = find_images_by_tag(self.docker_client,
                                    lambda tag: tag.startswith(self.test_environment.repository_name))
        self.assertTrue(len(images) > 0,
                        f"Did not found images for repository "
                        f"{self.test_environment.repository_name} in list {images}")


if __name__ == '__main__':
    unittest.main()
