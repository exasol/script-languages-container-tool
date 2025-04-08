import unittest

import exasol.bucketfs as bfs
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils


class DockerRunDBTestDockerDBTestNoCompression(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            self, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        self.itde_test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, False
        )
        self.test_environment.clean_images()
        self.docker_environment_name = self.__class__.__name__
        self.docker_environment = (
            self.itde_test_environment.spawn_docker_test_environment(
                self.docker_environment_name
            )
        )

    def tearDown(self):
        utils.close_environments(self.docker_environment, self.test_environment)

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

    def test_run_db_tests_docker_db(self):
        arguments = " ".join(
            [
                f"--environment-type external_db",
                f"--external-exasol-db-host {self.docker_environment.database_host}",
                f"--external-exasol-db-port {self.docker_environment.ports.database}",
                f"--external-exasol-bucketfs-port {self.docker_environment.ports.bucketfs}",
                f"--external-exasol-ssh-port {self.docker_environment.ports.ssh}",
                f"--external-exasol-db-user {self.docker_environment.db_username}",
                f"--external-exasol-db-password {self.docker_environment.db_password}",
                f"--external-exasol-bucketfs-write-password {self.docker_environment.bucketfs_password}",
                f"--compression-strategy none",
                exaslct_utils.get_full_test_container_folder_parameter(),
            ]
        )
        self.test_environment.run_command(
            f"{self.test_environment.executable} run-db-test {arguments}",
            track_task_dependencies=True,
        )

        self.validate_file_on_bucket_fs(f"test-flavor.tar")


if __name__ == "__main__":
    unittest.main()
