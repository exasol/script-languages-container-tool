import unittest

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils
from exasol_integration_test_docker_environment.testing.docker_registry import (
    LocalDockerRegistryContextManager,
)

from exasol.slc import api


class ApiDockerPushTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.test_environment.clean_all_images()

    def tearDown(self):
        utils.close_environments(self.test_environment)

    def test_docker_push(self):
        with LocalDockerRegistryContextManager(
            self.test_environment.name
        ) as local_registry:
            self.test_environment.docker_repository_name = local_registry.name
            image_infos = api.push(
                flavor_path=(str(exaslct_utils.get_test_flavor()),),
                source_docker_repository_name=self.test_environment.docker_repository_name,
                target_docker_repository_name=self.test_environment.docker_repository_name,
            )
            print("repos:", local_registry.repositories)
            self.assertIn(str(exaslct_utils.get_test_flavor()), image_infos)
            images = local_registry.images
            print("images", images)
            images_info_list = image_infos[str(exaslct_utils.get_test_flavor())]
            print("images_info_list", images_info_list)
            images_info_list_tags = sorted(
                list(
                    {
                        f"{image_info.target_tag}_{image_info.hash}"
                        for image_info in images_info_list
                    }
                )
            )
            self.assertEqual(
                sorted(images["tags"]),
                images_info_list_tags,
                f"{images} doesn't have the expected tags, it only has {len(images['tags'])}",
            )


if __name__ == "__main__":
    unittest.main()
