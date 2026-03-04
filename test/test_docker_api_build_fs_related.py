import unittest

import docker  # type: ignore
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc.api import build
from exasol.slc.internal.utils.docker_utils import find_images_by_tag


class ApiDockerBuildTestFlavorWithSymlink(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)
        utils.close_environments(self.test_environment)

    def test_docker_build(self):
        flavor_path = (
            exaslct_utils.get_file_system_related_flavors().symlink_test_flavor
        )
        image_infos = build(
            flavor_path=(str(flavor_path),),
            source_docker_repository_name=self.test_environment.docker_repository_name,
            target_docker_repository_name=self.test_environment.docker_repository_name,
        )
        assert len(image_infos) == 1
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        assert len(images) == 1


class ApiDockerBuildTestFlavorWithSpaces(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()

    def tearDown(self):
        try:
            self.docker_client.close()
        except Exception as e:
            print(e)
        utils.close_environments(self.test_environment)

    def test_docker_build(self):
        flavor_path = (
            exaslct_utils.get_file_system_related_flavors().test_flavor_with_spaces
        )
        image_infos = build(
            flavor_path=(str(flavor_path),),
            source_docker_repository_name=self.test_environment.docker_repository_name,
            target_docker_repository_name=self.test_environment.docker_repository_name,
        )
        assert len(image_infos) == 1
        images = find_images_by_tag(
            self.docker_client,
            lambda tag: tag.startswith(self.test_environment.docker_repository_name),
        )
        assert len(images) == 1


if __name__ == "__main__":
    unittest.main()
