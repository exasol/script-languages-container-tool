import subprocess
import tarfile
import unittest
from tempfile import TemporaryDirectory

import docker
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.data.environment_type import (
    EnvironmentType,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api


class ApiDockerRunDbTestNoCompression(unittest.TestCase):
    #
    # Spawn a Docker db and run tests.
    # The container will be exported and uploaded without compression.
    #
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

    def validate_file_on_bucket_fs(self, expected_file: str):
        host = self.docker_environment.database_host
        port = self.docker_environment.ports.bucketfs
        bucketfs_username = self.docker_environment.bucketfs_username
        bucketfs_password = self.docker_environment.bucketfs_password
        path_in_bucket = f"myudfs/{expected_file}"
        with TemporaryDirectory() as tmpdir:
            url = f"http://{bucketfs_username}:{bucketfs_password}@{host}:{port}/{path_in_bucket}"
            file_name = f"{tmpdir}/{expected_file}"
            cmd = [
                "curl",
                "--silent",
                "--show-error",
                "--fail",
                url,
                "--output",
                file_name,
            ]
            p = subprocess.run(cmd, capture_output=True)
            p.check_returncode()

            # "r:" makes 'tarfile.open' to raise an exception if file is not uncompressed tar format
            tar_mode = "r:"
            with tarfile.open(name=file_name, mode=tar_mode) as tf:  # type: ignore
                tf_members = tf.getmembers()
                last_tf_member = tf_members[-1]
                assert last_tf_member.name == "exasol-manifest.json"
                assert last_tf_member.path == "exasol-manifest.json"

    def test_run_db_test_no_compression(self):
        self._run_db_test()
        self.validate_file_on_bucket_fs(f"test-flavor.tar")


if __name__ == "__main__":
    unittest.main()
