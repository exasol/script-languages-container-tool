import subprocess
import tarfile
import unittest
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional

import exasol.bucketfs as bfs  # type: ignore
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.api_errors import (
    TaskRuntimeError,
)
from exasol_integration_test_docker_environment.testing import utils  # type: ignore

from exasol.slc import api
from exasol.slc.models.compression_strategy import CompressionStrategy
from exasol.slc.models.deploy_result import DeployResult


class ApiDockerDeployTest(unittest.TestCase):
    #
    # Test deploy API method with different options.
    #

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

    def _expected_file(self, release_name: str, extension: str = "") -> str:
        return f"test-flavor-release-{release_name}{extension}"

    def _build_bfs_path(
        self,
        bucket_name: str,
        bucketfs_name: str,
        expected_extension: str,
        path: Optional[str],
        release_name: str,
    ) -> bfs._path.PathLike:
        build_path_func = partial(
            bfs.path.build_path,
            backend=bfs.path.StorageBackend.onprem,
            url=f"http://{self.docker_environment.database_host}:{self.docker_environment.ports.bucketfs}",
            bucket_name=bucket_name,
            service_name=bucketfs_name,
            username="w",
            password=self.docker_environment.bucketfs_password,
            verify=False,
        )
        if path:
            expected_path_in_bucket = (
                build_path_func(path=path)
                / f"test-flavor-release-{release_name}{expected_extension}"
            )
        else:
            expected_path_in_bucket = (
                build_path_func()
                / f"test-flavor-release-{release_name}{expected_extension}"
            )
        return expected_path_in_bucket

    def _run_deploy(
        self,
        bucket_name: str,
        bucketfs_name: str,
        compression_strategy: CompressionStrategy,
        flavor_path: Path,
        path: Optional[str],
        release_name: str,
    ) -> dict[str, dict[str, DeployResult]]:
        deploy_func = partial(
            api.deploy,
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
            compression_strategy=compression_strategy,
        )
        if path:
            result = deploy_func(path_in_bucket=path)
        else:
            result = deploy_func()
        return result

    def _validate_deploy(
        self,
        compression_strategy: CompressionStrategy,
        path: Optional[str],
        expected_extension: str,
    ):
        release_name = "TEST"
        bucketfs_name = "bfsdefault"
        bucket_name = "default"
        flavor_path = exaslct_utils.get_test_flavor()
        result = self._run_deploy(
            bucket_name,
            bucketfs_name,
            compression_strategy,
            flavor_path,
            path,
            release_name,
        )

        self.assertIn(str(flavor_path), result.keys())
        self.assertEqual(len(result), 1)
        self.assertIn(str(flavor_path), result.keys())
        self.assertEqual(len(result[str(flavor_path)]), 1)

        deploy_result = result[str(flavor_path)]["release"]
        self.assertIn(
            f".build_output/cache/exports/test-flavor-release-",
            deploy_result.release_path,
        )

        self._validate_alter_session_cmd(
            bucket_name, bucketfs_name, deploy_result, path, release_name
        )
        self._validate_upload_path(
            bucket_name, deploy_result, expected_extension, path, release_name
        )

        expected_path_in_bucket = self._build_bfs_path(
            bucket_name, bucketfs_name, expected_extension, path, release_name
        )
        # Compare UDF path of `bucket_path` until bfs.path.PathLike implements comparison
        self.assertEqual(
            expected_path_in_bucket.as_udf_path(),
            deploy_result.bucket_path.as_udf_path(),
        )

        self.validate_file_on_bucket_fs(
            bucket_name,
            path,
            release_name,
            expected_extension,
            compression_strategy=compression_strategy,
        )

    def _validate_upload_path(
        self,
        bucket_name: str,
        deploy_result: DeployResult,
        expected_extension: str,
        path: Optional[str],
        release_name: str,
    ) -> None:
        upload_path = "/".join(
            [
                part
                for part in [
                    bucket_name,
                    path,
                    self._expected_file(release_name, expected_extension),
                ]
                if part is not None
            ]
        )
        self.assertEqual(
            deploy_result.human_readable_upload_location,
            f"http://{self.docker_environment.database_host}:{self.docker_environment.ports.bucketfs}/"
            f"{upload_path}",
        )

    def _validate_alter_session_cmd(
        self,
        bucket_name: str,
        bucketfs_name: str,
        deploy_result: DeployResult,
        path: Optional[str],
        release_name: str,
    ) -> None:
        complete_path_in_bucket = "/".join(
            [
                part
                for part in [
                    bucketfs_name,
                    bucket_name,
                    path,
                    self._expected_file(release_name),
                ]
                if part is not None
            ]
        )
        expected_alter_session_cmd = (
            f"ALTER SESSION SET SCRIPT_LANGUAGES='PYTHON3_TEST=localzmq+protobuf:///{complete_path_in_bucket}?lang=python#buckets/"
            f"{complete_path_in_bucket}/exaudf/exaudfclient_py3';"
        )
        result_alter_session_cmd = (
            deploy_result.language_definition_builder.generate_alter_session()
        )
        self.assertEqual(result_alter_session_cmd, expected_alter_session_cmd)

    def validate_file_on_bucket_fs(
        self,
        bucket_name: str,
        path: Optional[str],
        release_name: str,
        expected_extension: str,
        compression_strategy: CompressionStrategy,
    ):
        host = self.docker_environment.database_host
        port = self.docker_environment.ports.bucketfs
        bucketfs_username = self.docker_environment.bucketfs_username
        bucketfs_password = self.docker_environment.bucketfs_password
        expected_file = self._expected_file(release_name, expected_extension)
        path_in_bucket = "/".join(
            [part for part in [bucket_name, path, expected_file] if part is not None]
        )
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

            # "r:gz" / "r:" makes 'tarfile.open' to raise an exception if file is not in requested format
            tar_mode = (
                "r:gz" if compression_strategy == CompressionStrategy.GZIP else "r:"
            )
            with tarfile.open(name=file_name, mode=tar_mode) as tf:  # type: ignore
                tf_members = tf.getmembers()
                last_tf_member = tf_members[-1]
                assert last_tf_member.name == "exasol-manifest.json"
                assert last_tf_member.path == "exasol-manifest.json"

    def test_docker_api_deploy(self):
        self._validate_deploy(
            compression_strategy=CompressionStrategy.GZIP,
            path="test",
            expected_extension=".tar.gz",
        )

    def test_docker_api_deploy_no_compression(self):
        self._validate_deploy(
            compression_strategy=CompressionStrategy.NONE,
            path="test",
            expected_extension=".tar",
        )

    def test_docker_api_deploy_without_path_in_bucket(self):
        self._validate_deploy(
            compression_strategy=CompressionStrategy.GZIP,
            path=None,
            expected_extension=".tar.gz",
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


if __name__ == "__main__":
    unittest.main()
