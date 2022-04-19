import unittest

import docker
from exasol_script_languages_container_tool.cli.commands import build, clean_flavor_images

from exasol_script_languages_container_tool.lib.utils.docker_utils import find_images_by_tag
from click.testing import CliRunner

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import exaslct_test_environment


class DockerBuildDirectTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_test_environment.ExaslctTestEnvironment(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.docker_client = docker.from_env()
        self.runner = CliRunner()
        self._clean_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)
        self._clean_images()

    def _clean_images(self):
        self.runner.invoke(clean_flavor_images,
                           f"{self.test_environment.flavor_path_argument} "
                           f"{self.test_environment.clean_docker_repository_arguments}")

    def test_docker_build(self):
        """
        Test that executing any exaslct task multiple times within the same Python process,
        does not have any side effects.
        """

        for i in range(5):
            print(f"Execute build run: {i}.")
            result = self.runner.invoke(build, f"{self.test_environment.flavor_path_argument} "
                                               f"{self.test_environment.docker_repository_arguments}")
            assert result.exit_code == 0
        images = find_images_by_tag(self.docker_client,
                                    lambda tag: tag.startswith(self.test_environment.repository_name))
        self.assertTrue(len(images) > 0,
                        f"Did not found images for repository "
                        f"{self.test_environment.repository_name} in list {images}")


if __name__ == '__main__':
    unittest.main()
