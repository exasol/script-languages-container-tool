import re
import unittest
from pathlib import Path

import docker
from exasol_integration_test_docker_environment.lib.docker.container.utils import remove_docker_container
from exasol_integration_test_docker_environment.lib.docker.volumes.utils import remove_docker_volumes
from exasol_integration_test_docker_environment.lib.data.environment_info import EnvironmentInfo

import utils as exaslct_utils


class DockerRunDBTestDockerDBTestCheckArguments(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()
        self.client = docker.from_env()

    def tearDown(self):
        self.remove_docker_environment()
        self.test_environment.close()
        self.client.close()

    def _getEnvironmentInfo(self):
        test_environment_name = f"""{self.test_environment.flavor_path.name}_release"""
        environment_info_json_path = Path(self.test_environment.temp_dir,
                                          f"cache/environments/{test_environment_name}/environment_info.json")
        if environment_info_json_path.exists():
            with environment_info_json_path.open() as f:
                return EnvironmentInfo.from_json(f.read())

    def assert_mem_disk_size(self, mem_size: str, disk_size: str):
        env_info = self._getEnvironmentInfo()

        containers = \
            [c.name for c in
             self.client.containers.list()
             if env_info.database_info.container_info.container_name == c.name]
        self.assertEqual(len(containers), 1)
        exit_result = self.client.containers.get(containers[0]).exec_run("cat /exa/etc/EXAConf")
        output = exit_result[1].decode("UTF-8")
        if output == '':
            exit_result = self.client.containers.get(containers[0]).exec_run("cat /exa/etc/EXAConf")
            output = exit_result[1].decode("UTF-8")
            return_code = exit_result[0]
        return_code = exit_result[0]
        self.assertEqual(return_code, 0)
        """
        Mem-Size appearently gets modified by COS during startup (apparently since docker-db 7.1.7).
        We need to change the check and round the final value from the ExaConf in the docker db.
        """
        #Example "...{key} = 1.229 GiB...." => The regex extracts "1.229"
        mem_size_matches = re.findall(f"MemSize = (\d+\.\d+) GiB", output)
        self.assertEqual(len(mem_size_matches), 1)
        self.assertAlmostEqual(float(mem_size_matches[0]), float(mem_size), places=1)

        self.assertIn(f" Size = {disk_size}GiB", output)

    def remove_docker_environment(self):
        env_info = self._getEnvironmentInfo()
        remove_docker_container([env_info.test_container_info.container_name,
                                 env_info.database_info.container_info.container_name])
        volumes_to_remove = \
            [v for v in
             [env_info.test_container_info.volume_name,
              env_info.database_info.container_info.volume_name]
             if v is not None]
        remove_docker_volumes(volumes_to_remove)
        self._remove_docker_networks([env_info.network_info.network_name])

    def _remove_docker_networks(self, networks):
        for network in networks:
            try:
                self.client.networks.get(network).remove()
            except Exception as e:
                print(f"Error removing network:{e}")

    def test_run_db_tests_docker_db_disk_mem_size(self):
        mem_size = "1.3"
        disk_size = "1.4"
        arguments = " ".join([
            f"--test-file=empty_test.py",
            f"--db-mem-size={mem_size}GiB",
            f"--db-disk-size={disk_size}GiB",
            f"--reuse-test-environment",
            exaslct_utils.get_test_container_folder_for_tests_parameter()
        ])
        command = f"{self.test_environment.executable} run-db-test {arguments}"
        self.test_environment.run_command(
            command, track_task_dependencies=True)
        self.assert_mem_disk_size(mem_size, disk_size)


if __name__ == '__main__':
    unittest.main()
