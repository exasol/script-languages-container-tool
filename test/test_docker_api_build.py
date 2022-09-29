import unittest

import docker

from exasol_script_languages_container_tool.lib.api import build
from exasol_script_languages_container_tool.lib.utils.docker_utils import find_images_by_tag

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class ApiDockerBuildTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(self, True)
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)
        utils.close_environments(self.test_environment)

    def test_docker_build(self):
        image_infos = build(flavor_path=(str(self.test_environment.get_test_flavor()),),
                            source_docker_repository_name=self.test_environment.docker_repository_name,
                            target_docker_repository_name=self.test_environment.docker_repository_name)
        assert len(image_infos) == 1
        images = find_images_by_tag(self.docker_client,
                                    lambda tag: tag.startswith(self.test_environment.docker_repository_name))
        self.assertTrue(len(images) > 0,
                        f"Did not found images for repository "
                        f"{self.test_environment.docker_repository_name} in list {images}")
        image_infos_for_test_flavor = image_infos[str(self.test_environment.flavor_path)]
        for goal, image_info in image_infos_for_test_flavor.items():
            expected_prefix = f"{image_info.target_repository_name}:{image_info.target_tag}"
            images = find_images_by_tag(self.docker_client,
                                        lambda tag: tag.startswith(expected_prefix))
            self.assertTrue(len(images) == 1,
                            f"Did not found image for goal '{goal}' with prefix {expected_prefix} in list {images}")


if __name__ == '__main__':
    unittest.main()
