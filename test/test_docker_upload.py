import os
import subprocess
import unittest

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.testing import utils  # type: ignore


class DockerUploadTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print(f"SetUpClass: {cls.__name__}")
        cls.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(
            cls, exaslct_utils.EXASLCT_DEFAULT_BIN
        )
        cls.itde_test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            cls, False
        )
        cls.test_environment.clean_images()

        cls.docker_environment_name = cls.__name__
        cls.docker_environment = (
            cls.itde_test_environment.spawn_docker_test_environment(
                cls.docker_environment_name
            )
        )

    @classmethod
    def tearDownClass(cls):
        utils.close_environments(cls.docker_environment, cls.test_environment)

    def test_docker_upload_with_path_in_bucket(self):
        self.path_in_bucket = "test"
        self.release_name = "TEST"
        self.bucketfs_name = "bfsdefault"
        self.bucket_name = "default"
        arguments = " ".join(
            [
                f"--database-host {self.docker_environment.database_host}",
                f"--bucketfs-port {self.docker_environment.ports.bucketfs}",
                f"--bucketfs-username {self.docker_environment.bucketfs_username}",
                f"--bucketfs-password {self.docker_environment.bucketfs_password}",
                f"--bucketfs-name {self.bucketfs_name}",
                f"--bucket-name {self.bucket_name}",
                f"--path-in-bucket {self.path_in_bucket}",
                f"--no-bucketfs-https",
                f"--release-name {self.release_name}",
            ]
        )
        command = f"{self.test_environment.executable} upload {arguments}"

        completed_process = self.test_environment.run_command(
            command, track_task_dependencies=True, capture_output=True
        )
        self.assertIn(
            f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{self.bucketfs_name}/"
            f"{self.bucket_name}/{self.path_in_bucket}/test-flavor-release-{self.release_name}?lang=python#buckets/"
            f"{self.bucketfs_name}/{self.bucket_name}/{self.path_in_bucket}/test-flavor-release-{self.release_name}/"
            f"exaudf/exaudfclient_py3",
            completed_process.stdout.decode("UTF-8"),
        )
        self.validate_file_on_bucket_fs(
            f"{self.path_in_bucket}/test-flavor-release-{self.release_name}.tar.gz"
        )

    def test_docker_upload_without_path_in_bucket(self):
        self.release_name = "TEST"
        self.bucketfs_name = "bfsdefault"
        self.bucket_name = "default"
        arguments = " ".join(
            [
                f"--database-host {self.docker_environment.database_host}",
                f"--bucketfs-port {self.docker_environment.ports.bucketfs}",
                f"--bucketfs-username {self.docker_environment.bucketfs_username}",
                f"--bucketfs-password {self.docker_environment.bucketfs_password}",
                f"--bucketfs-name {self.bucketfs_name}",
                f"--bucket-name {self.bucket_name}",
                f"--no-bucketfs-https",
                f"--release-name {self.release_name}",
            ]
        )
        command = f"{self.test_environment.executable} upload {arguments}"

        completed_process = self.test_environment.run_command(
            command, track_task_dependencies=True, capture_output=True
        )
        self.assertIn(
            f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{self.bucketfs_name}/"
            f"{self.bucket_name}/test-flavor-release-{self.release_name}?lang=python#buckets/"
            f"{self.bucketfs_name}/{self.bucket_name}/test-flavor-release-{self.release_name}/exaudf/exaudfclient_py3",
            completed_process.stdout.decode("UTF-8"),
        )
        self.validate_file_on_bucket_fs(
            f"test-flavor-release-{self.release_name}.tar.gz"
        )

    def test_docker_upload_fail_path_in_bucket(self):
        self.release_name = "TEST"
        self.bucketfs_name = "bfsdefault"
        self.bucket_name = "default"
        arguments = " ".join(
            [
                f"--database-host {self.docker_environment.database_host}",
                f"--bucketfs-port {self.docker_environment.ports.bucketfs}",
                f"--bucketfs-username {self.docker_environment.bucketfs_username}",
                f"--bucketfs-password invalid",
                f"--bucketfs-name {self.bucketfs_name}",
                f"--bucket-name {self.bucket_name}",
                f"--no-bucketfs-https",
                f"--release-name {self.release_name}",
            ]
        )
        command = f"{self.test_environment.executable} upload {arguments}"

        exception_thrown = False
        try:
            self.test_environment.run_command(command, track_task_dependencies=True)
        except:
            exception_thrown = True
        assert exception_thrown

    def validate_file_on_bucket_fs(self, expected_file_path: str):
        url = "http://w:{password}@{host}:{port}/{bucket}".format(
            host=self.docker_environment.database_host,  # type: ignore
            port=self.docker_environment.ports.bucketfs,  # type: ignore
            bucket=self.bucket_name,
            password=self.docker_environment.bucketfs_password,  # type: ignore
        )
        cmd = ["curl", "--silent", "--show-error", "--fail", url]
        p = subprocess.run(cmd, capture_output=True)
        p.check_returncode()
        found_lines = [
            line
            for line in p.stdout.decode("utf-8").split("\n")
            if line == expected_file_path
        ]
        assert len(found_lines) == 1


if __name__ == "__main__":
    unittest.main()
