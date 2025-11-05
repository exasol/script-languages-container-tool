import subprocess
import tarfile
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

import exasol.bucketfs as bfs  # type: ignore
import utils as exaslct_utils  # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.api_errors import TaskRuntimeError

from exasol.slc import api
from exasol.slc.models.compression_strategy import CompressionStrategy
from exasol.slc.models.deploy_result import DeployResult

import pytest

@pytest.fixture
def test_environment():
    print("Setup test environment")
    env = exaslct_utils.ExaslctApiTestEnvironmentWithCleanup(None, True)
    env.clean_all_images()
    yield env
    print("Teardown test environment")
    # If you want to ensure cleanup regardless of test outcome use try/finally
    # This fixture scopes to function by default; change as needed
    # You can yield [env, docker_environment], or use more fixtures if used in parallel tests.

@pytest.fixture
def docker_environment(test_environment, request):
    docker_environment_name = request.node.name
    env = test_environment.spawn_docker_test_environment(docker_environment_name)
    yield env
    # Clean up environments in a fixture finalizer
    # utils.close_environments(test_environment, env)

def _expected_file(release_name: str, extension: str = "") -> str:
    return f"test-flavor-release-{release_name}{extension}"

def _build_bfs_path(
    docker_environment,
    bucket_name: str,
    bucketfs_name: str,
    expected_extension: str,
    path: Optional[str],
    release_name: str,
):
    build_path_func = partial(
        bfs.path.infer_path,
        bucketfs_host=docker_environment.database_host,
        bucketfs_port=docker_environment.ports.bucketfs,
        bucket=bucket_name,
        bucketfs_name=bucketfs_name,
        bucketfs_user="w",
        bucketfs_password=docker_environment.bucketfs_password,
        use_ssl_cert_validation=False,
    )
    if path:
        expected_path_in_bucket = (
            build_path_func(path=path) / f"test-flavor-release-{release_name}{expected_extension}"
        )
    else:
        expected_path_in_bucket = (
            build_path_func() / f"test-flavor-release-{release_name}{expected_extension}"
        )
    return expected_path_in_bucket

def _run_deploy(
    test_environment,
    docker_environment,
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
        bucketfs_host=docker_environment.database_host,
        bucketfs_port=docker_environment.ports.bucketfs,
        bucketfs_user=docker_environment.bucketfs_username,
        bucketfs_password=docker_environment.bucketfs_password,
        target_docker_repository_name=test_environment.docker_repository_name,
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

def _validate_upload_path(
    docker_environment,
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
                _expected_file(release_name, expected_extension),
            ]
            if part is not None
        ]
    )
    assert (
        deploy_result.human_readable_upload_location
        == f"http://{docker_environment.database_host}:{docker_environment.ports.bucketfs}/"
           f"{upload_path}"
    )

def _validate_alter_session_cmd(
    docker_environment,
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
                _expected_file(release_name),
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
    assert result_alter_session_cmd == expected_alter_session_cmd

def validate_file_on_bucket_fs(
    docker_environment,
    bucket_name: str,
    path: Optional[str],
    release_name: str,
    expected_extension: str,
    compression_strategy: CompressionStrategy,
):
    host = docker_environment.database_host
    port = docker_environment.ports.bucketfs
    bucketfs_username = docker_environment.bucketfs_username
    bucketfs_password = docker_environment.bucketfs_password
    expected_file = _expected_file(release_name, expected_extension)
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

        tar_mode = "r:gz" if compression_strategy == CompressionStrategy.GZIP else "r:"
        with tarfile.open(name=file_name, mode=tar_mode) as tf:  # type: ignore
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"

def _validate_deploy(
    test_environment,
    docker_environment,
    compression_strategy: CompressionStrategy,
    path: Optional[str],
    expected_extension: str,
):
    release_name = "TEST"
    bucketfs_name = "bfsdefault"
    bucket_name = "default"
    flavor_path = exaslct_utils.get_test_flavor()
    result = _run_deploy(
        test_environment,
        docker_environment,
        bucket_name,
        bucketfs_name,
        compression_strategy,
        flavor_path,
        path,
        release_name,
    )

    assert str(flavor_path) in result.keys()
    assert len(result) == 1
    assert str(flavor_path) in result.keys()
    assert len(result[str(flavor_path)]) == 1

    deploy_result = result[str(flavor_path)]["release"]
    assert f".build_output/cache/exports/test-flavor-release-" in deploy_result.release_path

    _validate_alter_session_cmd(
        docker_environment, bucket_name, bucketfs_name, deploy_result, path, release_name
    )
    _validate_upload_path(
        docker_environment, bucket_name, deploy_result, expected_extension, path, release_name
    )

    expected_path_in_bucket = _build_bfs_path(
        docker_environment, bucket_name, bucketfs_name, expected_extension, path, release_name
    )
    assert (
        expected_path_in_bucket.as_udf_path()
        == deploy_result.bucket_path.as_udf_path()
    )

    validate_file_on_bucket_fs(
        docker_environment,
        bucket_name,
        path,
        release_name,
        expected_extension,
        compression_strategy=compression_strategy,
    )

@pytest.mark.usefixtures("test_environment")
def test_docker_api_deploy(test_environment, docker_environment):
    _validate_deploy(
        test_environment,
        docker_environment,
        compression_strategy=CompressionStrategy.GZIP,
        path="test",
        expected_extension=".tar.gz",
    )

@pytest.mark.usefixtures("test_environment")
def test_docker_api_deploy_no_compression(test_environment, docker_environment):
    _validate_deploy(
        test_environment,
        docker_environment,
        compression_strategy=CompressionStrategy.NONE,
        path="test",
        expected_extension=".tar",
    )

@pytest.mark.usefixtures("test_environment")
def test_docker_api_deploy_without_path_in_bucket(test_environment, docker_environment):
    _validate_deploy(
        test_environment,
        docker_environment,
        compression_strategy=CompressionStrategy.GZIP,
        path=None,
        expected_extension=".tar.gz",
    )

@pytest.mark.usefixtures("test_environment")
def test_docker_api_deploy_fail_path_in_bucket(test_environment, docker_environment):
    release_name = "TEST"
    bucketfs_name = "bfsdefault"
    bucket_name = "default"
    with pytest.raises(TaskRuntimeError):
        api.deploy(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            bucketfs_host=docker_environment.database_host,
            bucketfs_port=docker_environment.ports.bucketfs,
            bucketfs_user=docker_environment.bucketfs_username,
            bucketfs_password="invalid",
            bucketfs_use_https=False,
            bucketfs_name=bucketfs_name,
            bucket=bucket_name,
            release_name=release_name,
        )
