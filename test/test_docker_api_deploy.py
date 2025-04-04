import subprocess
import tarfile
import unittest
from tempfile import TemporaryDirectory

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
            compression=compression,
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
            bucket_name,
            "",
            f"test-flavor-release-{release_name}.tar.gz",
            compression=False,
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

    # def check_file_in_bucketfs(
    #     self,
    #     url: str,
    #     bucket_name: str,
    #     bucketfs_username: str,
    #     bucketfs_password: str,
    #     path: str,
    #     expected_file: str,
    #     compression: bool,
    # ):
    #     CREDENTIALS = {
    #         bucket_name: {"username": bucketfs_username, "password": bucketfs_password}
    #     }
    #
    #     bucketfs = Service(url, CREDENTIALS)
    #     bucket = bucketfs[bucket_name]
    #
    #     with TemporaryDirectory() as tmpdir:
    #         file = as_file(
    #             bucket.download(f"{path}/{expected_file}"),
    #             filename=Path(tmpdir) / expected_file,
    #         )
    #
    #         tar_mode = "r:gz" if compression else "r:"
    #         with tarfile.open(name=file, mode=tar_mode) as tf:
    #             tf_members = tf.getmembers()
    #             last_tf_member = tf_members[-1]
    #             assert last_tf_member.name == "exasol-manifest.json"
    #             assert last_tf_member.path == "exasol-manifest.json"

    def check_file_in_bucketfs(
        self,
        host: str,
        port: int,
        bucket_name: str,
        bucketfs_username: str,
        bucketfs_password: str,
        path: str,
        expected_file: str,
        compression: bool,
    ):
        with TemporaryDirectory() as tmpdir:
            if path:
                url = f"http://{bucketfs_username}:{bucketfs_password}@{host}:{port}/{bucket_name}/{path}/{expected_file}"
            else:
                url = f"http://{bucketfs_username}:{bucketfs_password}@{host}:{port}/{bucket_name}/{expected_file}"
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

            tar_mode = "r:gz" if compression else "r:"
            with tarfile.open(name=file_name, mode=tar_mode) as tf:  # type: ignore
                tf_members = tf.getmembers()
                last_tf_member = tf_members[-1]
                assert last_tf_member.name == "exasol-manifest.json"
                assert last_tf_member.path == "exasol-manifest.json"

    def validate_file_on_bucket_fs(
        self, bucket_name: str, path: str, expected_file: str, compression: bool
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

        self.check_file_in_bucketfs(
            host=host,
            port=port,
            bucket_name=bucket_name,
            bucketfs_username=bucketfs_username,
            bucketfs_password=bucketfs_password,
            path=path,
            expected_file=expected_file,
            compression=compression,
        )


if __name__ == "__main__":
    unittest.main()
