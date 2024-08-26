import os
import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing.docker_registry import (
    LocalDockerRegistryContextManager,
)


class DockerPullTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.test_environment.clean_images()

    def tearDown(self):
        self.test_environment.close()

    def test_docker_pull(self):
        with LocalDockerRegistryContextManager(
            name=self.test_environment.name
        ) as local_registry:
            self.test_environment.repository_name = local_registry.name
            self.test_environment.clean_images()
            command = f"{self.test_environment.executable} push "
            self.test_environment.run_command(command, track_task_dependencies=False)
            self.test_environment.clean_images()
            command = f"{self.test_environment.executable} build "
            self.test_environment.run_command(command, track_task_dependencies=True)
            docker_pull_image_tasks = self.find_all(
                "timers", "DockerPullImageTask", self.test_environment.temp_dir
            )
            print(docker_pull_image_tasks)
            self.assertEqual(
                len(docker_pull_image_tasks),
                3,
                f"{docker_pull_image_tasks} doesn't contain the expected 3 docker_pull_image_tasks",
            )

    def find_all(self, search_root, search_name, path):
        result = []
        for root, dirs, files in os.walk(path):
            if search_root in root:
                for file in files:
                    if search_name in file:
                        result.append(os.path.join(root, file))
                for dir in dirs:
                    if search_name in dir:
                        result.append(os.path.join(root, dir))
        return result


if __name__ == "__main__":
    unittest.main()
