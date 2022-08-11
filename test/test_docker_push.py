import unittest

from exasol_integration_test_docker_environment.testing.docker_registry import LocalDockerRegistryContextManager

import utils as exaslct_utils


class DockerPushTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()

    def tearDown(self):
        self.test_environment.close()

    def test_docker_push(self):
        with LocalDockerRegistryContextManager(self.test_environment.name) as local_registry:
            command = f"{self.test_environment.executable} push "
            self.test_environment.run_command(command, track_task_dependencies=True)
            print("repos:", local_registry.repositories)
            images = local_registry.images
            print("images", images)
            self.assertEqual(len(images["tags"]), 10,
                             f"{images} doesn't have the expected 10 tags, it only has {len(images['tags'])}")


if __name__ == '__main__':
    unittest.main()
