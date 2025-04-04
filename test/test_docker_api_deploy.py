import subprocess
import unittest

import exasol.bucketfs as bfs  # type: ignore
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.api_errors import (
    TaskRuntimeError,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api


class ApiDockerDeployTest(unittest.TestCase):

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
        utils.close_environments(self.test_environment, self.docker_environment)

    def _validate_deploy(self, compression: bool, expected_extension: str):
        path_in_bucket = "test"
        release_name = "TEST"
        bucketfs_name = "bfsdefault"
        bucket_name = "default"
        flavor_path = exaslct_utils.get_test_flavor()
        result = api.deploy(
            flavor_path=(str(flavor_path),),
            bucketfs_host=self.docker_environment.database_host,
            bucketfs_port=self.docker_environment.ports.bucketfs,
            bucketfs_user=self.docker_environment.bucketfs_username,
            bucketfs_password=self.docker_environment.bucketfs_password,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            bucketfs_use_https=False,
            bucketfs_name=bucketfs_name,
            bucket=bucket_name,
            path_in_bucket=path_in_bucket,
            release_name=release_name,
            compression=compression,
        )
        self.assertIn(str(flavor_path), result.keys())

        self.assertEqual(len(result), 1)
        self.assertIn(str(flavor_path), result.keys())
        self.assertEqual(len(result[str(flavor_path)]), 1)
        deploy_result = result[str(flavor_path)]["release"]
        expected_alter_session_cmd = (
            f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{bucketfs_name}/"
            f"{bucket_name}/{path_in_bucket}/test-flavor-release-{release_name}?lang=python#buckets/"
            f"{bucketfs_name}/{bucket_name}/{path_in_bucket}/test-flavor-release-{release_name}/"
            f"exaudf/exaudfclient_py3';"
        )
        result_alter_session_cmd = (
            deploy_result.language_definition_builder.generate_alter_session()
        )

        self.assertEqual(result_alter_session_cmd, expected_alter_session_cmd)

        self.assertIn(
            f".build_output/cache/exports/test-flavor-release-",
            deploy_result.release_path,
        )

        self.assertEqual(
            deploy_result.human_readable_upload_location,
            f"http://{self.docker_environment.database_host}:{self.docker_environment.ports.bucketfs}/"
            f"{bucket_name}/{path_in_bucket}/test-flavor-release-{release_name}{expected_extension}",
        )

        expected_path_in_bucket = (
            bfs.path.build_path(
                backend=bfs.path.StorageBackend.onprem,
                url=f"http://{self.docker_environment.database_host}:{self.docker_environment.ports.bucketfs}",
                bucket_name=bucket_name,
                service_name=bucketfs_name,
                username="w",
                password=self.docker_environment.bucketfs_password,
                verify=False,
                path=path_in_bucket,
            )
            / f"test-flavor-release-{release_name}{expected_extension}"
        )

        # Compare UDF path of `bucket_path` until bfs.path.PathLike implements comparison
        self.assertEqual(
            expected_path_in_bucket.as_udf_path(),
            deploy_result.bucket_path.as_udf_path(),
        )

        self.validate_file_on_bucket_fs(
            bucket_name,
            path_in_bucket,
            f"test-flavor-release-{release_name}{expected_extension}",
        )

    def test_docker_api_deploy(self):
        self._validate_deploy(compression=True, expected_extension=".tar.gz")

    def test_docker_api_deploy_no_compression(self):
        self._validate_deploy(compression=False, expected_extension=".tar")

    def test_docker_api_deploy_without_path_in_bucket(self):
        release_name = "TEST"
        bucketfs_name = "bfsdefault"
        bucket_name = "default"
        flavor_path = exaslct_utils.get_test_flavor()
        result = api.deploy(
            flavor_path=(str(flavor_path),),
            bucketfs_host=self.docker_environment.database_host,
            bucketfs_port=self.docker_environment.ports.bucketfs,
            bucketfs_user=self.docker_environment.bucketfs_username,
            bucketfs_password=self.docker_environment.bucketfs_password,
            target_docker_repository_name=self.test_environment.docker_repository_name,
            bucketfs_use_https=False,
            bucketfs_name=bucketfs_name,
            bucket=bucket_name,
            release_name=release_name,
        )
        self.assertIn(str(flavor_path), result.keys())
        self.assertEqual(len(result), 1)
        self.assertIn(str(flavor_path), result.keys())
        self.assertEqual(len(result[str(flavor_path)]), 1)
        deploy_result = result[str(flavor_path)]["release"]
        expected_alter_session_cmd = (
            f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{bucketfs_name}/"
            f"{bucket_name}/test-flavor-release-{release_name}?lang=python#buckets/"
            f"{bucketfs_name}/{bucket_name}/test-flavor-release-{release_name}/"
            f"exaudf/exaudfclient_py3';"
        )
        result_alter_session_cmd = (
            deploy_result.language_definition_builder.generate_alter_session()
        )
        self.assertEqual(result_alter_session_cmd, expected_alter_session_cmd)

        self.assertIn(
            f".build_output/cache/exports/test-flavor-release-",
            deploy_result.release_path,
        )

        self.assertEqual(
            deploy_result.human_readable_upload_location,
            f"http://{self.docker_environment.database_host}:{self.docker_environment.ports.bucketfs}/"
            f"{bucket_name}/test-flavor-release-{release_name}.tar.gz",
        )

        expected_path_in_bucket = (
            bfs.path.build_path(
                backend=bfs.path.StorageBackend.onprem,
                url=f"http://{self.docker_environment.database_host}:{self.docker_environment.ports.bucketfs}",
                bucket_name=bucket_name,
                service_name=bucketfs_name,
                username="w",
                password=self.docker_environment.bucketfs_password,
                verify=False,
            )
            / f"test-flavor-release-{release_name}.tar.gz"
        )

        # Compare UDF path of `bucket_path` until bfs.path.PathLike implements comparison
        self.assertEqual(
            expected_path_in_bucket.as_udf_path(),
            deploy_result.bucket_path.as_udf_path(),
        )

        self.validate_file_on_bucket_fs(
            bucket_name, "", f"test-flavor-release-{release_name}.tar.gz"
        )

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

    def validate_file_on_bucket_fs(
        self, bucket_name: str, path: str, expected_file: str
    ):
        host = self.docker_environment.database_host
        port = self.docker_environment.ports.bucketfs
        bucketfs_username = self.docker_environment.bucketfs_username
        bucketfs_password = self.docker_environment.bucketfs_password
        url = f"http://{host}:{port}"
        udf_path = bfs.path.build_path(
            backend=bfs.path.StorageBackend.onprem,
            url=url,
            bucket_name=bucket_name,
            service_name="bfsdefault",
            path=path,
            username=bucketfs_username,
            password=bucketfs_password,
            verify=True,
        )

        container_files = [
            file for file in udf_path.iterdir() if file.name == expected_file
        ]
        self.assertEqual(len(container_files), 1)


if __name__ == "__main__":
    unittest.main()
