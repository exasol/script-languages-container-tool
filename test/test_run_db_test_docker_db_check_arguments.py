import unittest
import docker
import os.path
from exasol_integration_test_docker_environment.test import utils

import utils as exaslct_utils


class DockerRunDBTestDockerDBTestCheckArguments(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = utils.ExaslctTestEnvironment(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()
        arguments = [
            f"--db-mem-size=1.3GiB",
            f"--db-disk-size=1.3GiB"
        ]
        self.client = docker.from_env()

    def tearDown(self):
        pass
        #self.remove_docker_container()
        #self.test_environment.close()

    def _getEnvironmentInfo(self):
        env_path = os.path.join(self.test_environment.temp_dir, "cache", "environments", self.test_environment.flavor_path.name)
        print(f"THOMAS:{env_path}")

    def assert_mem_size(self, size: str):
        containers = [c.name for c in self.client.containers.list() if self.docker_environment_name in c.name]
        db_container = [c for c in containers if "db_container" in c]
        exit_result = self.client.containers.get(db_container[0]).exec_run("cat /exa/etc/EXAConf")
        output = exit_result[1].decode("UTF-8")
        if output == '':
            exit_result = self.client.containers.get(db_container[0]).exec_run("cat /exa/etc/EXAConf")
            output = exit_result[1].decode("UTF-8")
            return_code = exit_result[0]
        return_code = exit_result[0]
        self.assertEquals(return_code, 0)
        self.assertIn("MemSize = %s" % size, output)

    def remove_docker_container(self):
        utils.remove_docker_container([f"test_container_test-flavor_release",
                                       f"db_container_test-flavor_release"])
        utils.remove_docker_volumes([f"db_container_test-flavor_release_volume"])

    def test_run_db_tests_docker_db(self):
        arguments = " ".join([
            f"--test-file=empty_test.py",
            f"--reuse-test-environment"
        ])
        command = f"{self.test_environment.executable} run-db-test {arguments}"
        self.test_environment.run_command(
            command, track_task_dependencies=True)
        #self.assert_mem_size("1.3GiB")
        self._getEnvironmentInfo()


if __name__ == '__main__':
    unittest.main()
