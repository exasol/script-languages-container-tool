import subprocess
import unittest

import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.api.api_errors import (
    TaskRuntimeError,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore
from exasol_integration_test_docker_environment.testing.docker_registry import (
    LocalDockerRegistryContextManager,
)  # type: ignore

from exasol_script_languages_container_tool.lib import api


class ApiDockerPushTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(
            self, True
        )
        self.test_environment.clean_all_images()
        self.docker_environment_name = self.__class__.__name__
        self.docker_environment = self.test_environment.spawn_docker_test_environment(
            self.docker_environment_name
        )

    def tearDown(self):
        utils.close_environments(self.test_environment)

    # def test_docker_api_deploy(self):
    #     path_in_bucket = "test"
    #     release_name = "TEST"
    #     bucketfs_name = "bfsdefault"
    #     bucket_name = "default"
    #     result = api.deploy(
    #         flavor_path=(str(exaslct_utils.get_test_flavor()),),
    #         bucketfs_host=self.docker_environment.database_host,
    #         bucketfs_port=self.docker_environment.ports.bucketfs,
    #         bucketfs_user=self.docker_environment.bucketfs_username,
    #         bucketfs_password=self.docker_environment.bucketfs_password,
    #         bucketfs_use_https=False,
    #         bucketfs_name=bucketfs_name,
    #         bucket=bucket_name,
    #         path_in_bucket=path_in_bucket,
    #         release_name=release_name,
    #     )
    #     with result.open("r") as f:
    #         res = f.read()
    #     self.assertIn(
    #         f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{bucketfs_name}/"
    #         f"{bucket_name}/{path_in_bucket}/test-flavor-release-{release_name}?lang=python#buckets/"
    #         f"{bucketfs_name}/{bucket_name}/{path_in_bucket}/test-flavor-release-{release_name}/"
    #         f"exaudf/exaudfclient_py3",
    #         res,
    #     )
    #     self.validate_file_on_bucket_fs(
    #         bucket_name, f"{path_in_bucket}/test-flavor-release-{release_name}.tar.gz"
    #     )
    #
    # def test_docker_api_deploy_without_path_in_bucket(self):
    #     release_name = "TEST"
    #     bucketfs_name = "bfsdefault"
    #     bucket_name = "default"
    #     result = api.deploy(
    #         flavor_path=(str(exaslct_utils.get_test_flavor()),),
    #         bucketfs_host=self.docker_environment.database_host,
    #         bucketfs_port=self.docker_environment.ports.bucketfs,
    #         bucketfs_user=self.docker_environment.bucketfs_username,
    #         bucketfs_password=self.docker_environment.bucketfs_password,
    #         bucketfs_use_https=False,
    #         bucketfs_name=bucketfs_name,
    #         bucket=bucket_name,
    #         release_name=release_name,
    #     )
    #     with result.open("r") as f:
    #         res = f.read()
    #     self.assertIn(
    #         f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{bucketfs_name}/"
    #         f"{bucket_name}/test-flavor-release-{release_name}?lang=python#buckets/"
    #         f"{bucketfs_name}/{bucket_name}/test-flavor-release-{release_name}/"
    #         f"exaudf/exaudfclient_py3",
    #         res,
    #     )
    #     self.validate_file_on_bucket_fs(
    #         bucket_name, f"test-flavor-release-{release_name}.tar.gz"
    #     )

    def test_docker_api_deploy_fail_path_in_bucket(self):
        release_name = "TEST"
        bucketfs_name = "bfsdefault"
        bucket_name = "default"
        exception_thrown = False
        try:
            result = api.deploy(
                flavor_path=(str(exaslct_utils.get_test_flavor()),),
                bucketfs_host=self.docker_environment.database_host,
                bucketfs_port=self.docker_environment.ports.bucketfs,
                bucketfs_user=self.docker_environment.bucketfs_username,
                bucketfs_password="invalid",
                bucketfs_use_https=False,
                bucketfs_name=bucketfs_name,
                bucket=bucket_name,
                release_name=release_name,
            )
        except TaskRuntimeError:
            exception_thrown = True
        assert exception_thrown

    def validate_file_on_bucket_fs(self, bucket_name: str, expected_file_path: str):
        url = "http://w:{password}@{host}:{port}/{bucket}".format(
            host=self.docker_environment.database_host,  # type: ignore
            port=self.docker_environment.ports.bucketfs,  # type: ignore
            bucket=bucket_name,
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
