import unittest

import docker
import exasol.bucketfs as bfs
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.data.environment_type import (
    EnvironmentType,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api


class ApiDockerRunDbTestNoCompression(unittest.TestCase):
    #
    # Spawn a
    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.export_path = self.test_environment.temp_dir + "/export_dir"
        self.docker_client = docker.from_env()
        self.test_environment.clean_all_images()
        docker_environment_name = self.test_environment.name
        self.docker_environment = self.test_environment.spawn_docker_test_environment(
            docker_environment_name
        )

    def tearDown(self):
        utils.close_environments(self.test_environment, self.docker_environment)

    def _run_db_test(self):
        api.run_db_test(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            test_container_folder=str(exaslct_utils.get_full_test_container_folder()),
            output_directory=self.test_environment.output_dir,
            compression=False,
            external_exasol_db_host=self.docker_environment.database_host,
            external_exasol_db_port=self.docker_environment.ports.database,
            external_exasol_db_user=self.docker_environment.db_username,
            external_exasol_db_password=self.docker_environment.db_password,
            external_exasol_bucketfs_port=self.docker_environment.ports.bucketfs,
            external_exasol_bucketfs_write_password=self.docker_environment.bucketfs_password,
            external_exasol_ssh_port=self.docker_environment.ports.ssh,
            environment_type=EnvironmentType.external_db.name,
        )

    def validate_file_on_bucket_fs(self, expected_file_path: str):
        host = self.docker_environment.database_host
        port = self.docker_environment.ports.bucketfs
        bucketfs_username = self.docker_environment.bucketfs_username
        bucketfs_password = self.docker_environment.bucketfs_password
        url = f"http://{host}:{port}"
        udf_path = bfs.path.build_path(
            backend=bfs.path.StorageBackend.onprem,
            url=url,
            bucket_name="myudfs",
            service_name="bfsdefault",
            username=bucketfs_username,
            password=bucketfs_password,
            verify=True,
        )

        container_files = [
            file for file in udf_path.iterdir() if file.name == expected_file_path
        ]
        self.assertEqual(len(container_files), 1)

    def test_run_db_test_no_compression(self):
        self._run_db_test()
        self.validate_file_on_bucket_fs(f"test-flavor.tar")


if __name__ == "__main__":
    unittest.main()
