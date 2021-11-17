import os
import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class DockerUploadTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()
        self.docker_environment_name = self.__class__.__name__
        self.docker_environments = \
            self.test_environment.spawn_docker_test_environments(self.docker_environment_name)
        if "GOOGLE_CLOUD_BUILD" in os.environ:
            self.docker_environment = self.docker_environments.google_cloud_environment
        else:
            self.docker_environment = self.docker_environments.on_host_docker_environment

    def tearDown(self):
        utils.close_environments(self.docker_environments, self.test_environment)

    def test_docker_upload_with_path_in_bucket(self):
        self.path_in_bucket = "test"
        self.release_name = "TEST"
        self.bucketfs_name = "bfsdefault"
        self.bucket_name = "default"
        arguments = " ".join([
            f"--database-host {self.docker_environment.database_host}",
            f"--bucketfs-port {self.docker_environment.bucketfs_port}",
            f"--bucketfs-username {self.docker_environment.bucketfs_username}",
            f"--bucketfs-password {self.docker_environment.bucketfs_password}",
            f"--bucketfs-name {self.bucketfs_name}",
            f"--bucket-name {self.bucket_name}",
            f"--path-in-bucket {self.path_in_bucket}",
            f"--no-bucketfs-https",
            f"--release-name {self.release_name}",
        ])
        command = f"{self.test_environment.executable} upload {arguments}"

        self.test_environment.run_command(command, track_task_dependencies=True)

    def test_docker_upload_without_path_in_bucket(self):
        self.release_name = "TEST"
        self.bucketfs_name = "bfsdefault"
        self.bucket_name = "default"
        arguments = " ".join([
            f"--database-host {self.docker_environment.database_host}",
            f"--bucketfs-port {self.docker_environment.bucketfs_port}",
            f"--bucketfs-username {self.docker_environment.bucketfs_username}",
            f"--bucketfs-password {self.docker_environment.bucketfs_password}",
            f"--bucketfs-name {self.bucketfs_name}",
            f"--bucket-name {self.bucket_name}",
            f"--no-bucketfs-https",
            f"--release-name {self.release_name}",
        ])
        command = f"{self.test_environment.executable} upload {arguments}"

        completed_process = self.test_environment.run_command(command, track_task_dependencies=True, capture_output=True)

        self.assertIn(
            f"ALTER SESSION SET SCRIPT_LANGUAGES=\'PYTHON3=localzmq+protobuf:///{self.bucketfs_name}/{self.bucket_name}/test-flavor-release-{self.release_name}?lang=python#buckets/{self.bucketfs_name}/{self.bucket_name}/test-flavor-release-{self.release_name}/exaudf/exaudfclient_py3",
            completed_process.stdout.decode("UTF-8"))

    def test_docker_upload_fail_path_in_bucket(self):
        self.release_name = "TEST"
        self.bucketfs_name = "bfsdefault"
        self.bucket_name = "default"
        arguments = " ".join([
            f"--database-host {self.docker_environment.database_host}",
            f"--bucketfs-port {self.docker_environment.bucketfs_port}",
            f"--bucketfs-username {self.docker_environment.bucketfs_username}",
            f"--bucketfs-password invalid",
            f"--bucketfs-name {self.bucketfs_name}",
            f"--bucket-name {self.bucket_name}",
            f"--no-bucketfs-https",
            f"--release-name {self.release_name}",
        ])
        command = f"{self.test_environment.executable} upload {arguments}"

        exception_thrown = False
        try:
            self.test_environment.run_command(command, track_task_dependencies=True)
        except:
            exception_thrown = True
        assert exception_thrown


if __name__ == '__main__':
    unittest.main()
