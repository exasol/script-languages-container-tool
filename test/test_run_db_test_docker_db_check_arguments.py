import re
import unittest
from io import StringIO
from pathlib import Path

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from configobj import ConfigObj
from exasol_integration_test_docker_environment.lib.docker.container.utils import (
    remove_docker_container,
)
from exasol_integration_test_docker_environment.lib.docker.volumes.utils import (
    remove_docker_volumes,
)
from exasol_integration_test_docker_environment.lib.models.data.environment_info import (
    EnvironmentInfo,
)


class DockerRunDBTestDockerDBTestCheckArguments(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.test_environment.clean_images()
        self.client = docker.from_env()

    def tearDown(self):
        self.remove_docker_environment()
        self.test_environment.close()
        self.client.close()

    def _get_environment_info(self):
        test_environment_name = f"""{self.test_environment.flavor_path.name}_release"""
        environment_info_json_path = Path(
            self.test_environment.temp_dir,
            f"cache/environments/{test_environment_name}/environment_info.json",
        )
        if environment_info_json_path.exists():
            with environment_info_json_path.open() as f:
                return EnvironmentInfo.from_json(f.read())
        else:
            raise FileNotFoundError(
                f"Environment info not found at {environment_info_json_path}"
            )

    def assert_mem_disk_size(self, mem_size: str, disk_size: str):
        env_info = self._get_environment_info()

        containers = [
            c.name
            for c in self.client.containers.list()
            if env_info.database_info.container_info.container_name == c.name
        ]
        self.assertEqual(len(containers), 1)
        exit_result = self.client.containers.get(containers[0]).exec_run(
            "cat /exa/etc/EXAConf"
        )
        output = exit_result[1].decode("UTF-8")
        if output == "":
            exit_result = self.client.containers.get(containers[0]).exec_run(
                "cat /exa/etc/EXAConf"
            )
            output = exit_result[1].decode("UTF-8")
            return_code = exit_result[0]
        return_code = exit_result[0]
        self.assertEqual(return_code, 0)
        """
        The size values might be modified by COS during startup (apparently since docker-db 7.1.7).
        We need to allow zero or more whitespace between the numbder and the unit.
        Further, we need to compare the number after rounding.
        """
        config = ConfigObj(StringIO(output))

        mem_size_value = config["DB : DB1"]["MemSize"]
        mem_size_matches = re.findall(r"(\d+\.\d+)\s*GiB", mem_size_value)
        self.assertEqual(len(mem_size_matches), 1)
        self.assertAlmostEqual(float(mem_size_matches[0]), float(mem_size), places=1)

        disk_size_value = config["EXAVolume : DataVolume1"]["Size"]
        disk_size_matches = re.findall(r"(\d+\.\d+)\s*GiB", disk_size_value)
        self.assertEqual(len(disk_size_matches), 1)
        self.assertAlmostEqual(float(disk_size_matches[0]), float(disk_size), places=1)

    def remove_docker_environment(self):
        env_info = self._get_environment_info()
        remove_docker_container(
            [
                env_info.test_container_info.container_name,
                env_info.database_info.container_info.container_name,
            ]
        )
        volumes_to_remove = [
            v
            for v in [
                env_info.test_container_info.volume_name,
                env_info.database_info.container_info.volume_name,
            ]
            if v is not None
        ]
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
        arguments = " ".join(
            [
                f"--test-file=empty_test.py",
                f"--db-mem-size={mem_size}GiB",
                f"--db-disk-size={disk_size}GiB",
                f"--reuse-test-environment",
                exaslct_utils.get_full_test_container_folder_parameter(),
            ]
        )
        command = f"{self.test_environment.executable} run-db-test {arguments}"
        self.test_environment.run_command(command, track_task_dependencies=True)
        self.assert_mem_disk_size(mem_size, disk_size)


if __name__ == "__main__":
    unittest.main()
