from tempfile import TemporaryDirectory
import tarfile

import test.utils as exaslct_utils # type: ignore # pylint: disable=import-error
from exasol_integration_test_docker_environment.lib.models.api_errors import TaskRuntimeError
import pytest
import exasol.bucketfs as bfs # type: ignore
from functools import partial
from typing import Optional
from pathlib import Path
from exasol.slc import api
from exasol.slc.models.deploy_result import DeployResult
from exasol.slc.models.compression_strategy import CompressionStrategy
from exasol.bucketfs._path import StorageBackend
# @pytest.fixture
# def require_saas_bucketfs_params(backend_aware_saas_bucketfs_params, use_saas):
#     if not use_saas:
#         pytest.skip("Skipped as SaaS backend is not selected")
#     return backend_aware_saas_bucketfs_params

@pytest.fixture
def require_saas_bucketfs_params():
    backend_aware_saas_bucketfs_params = {
        "url":"https://cloud-staging.exasol.com",
        "account_id":"org_KBcBm3nqUi0iqWq2",
        "database_id":"gkvt0tb-TzKT4tTxXmDxDQ",
        "pat":"exa_pat_6jXq3wX2HVHrgWQhTyAGXPRJBrkH9vGh3qr92J6d0noXm3"
    }
    return backend_aware_saas_bucketfs_params

def _expected_file(release_name: str, extension: str = "") -> str:
    return f"test-flavor-release-{release_name}{extension}"

def _build_bfs_path(
        require_saas_bucketfs_params,release_name:str,expected_extension:str

) -> bfs.path.PathLike:
    saas_params = require_saas_bucketfs_params
    return bfs.path.build_path(
        backend=StorageBackend.saas,
        url=saas_params["url"],
        account_id=saas_params["account_id"],
        database_id=saas_params["database_id"],
        pat=saas_params["pat"],
        path="saastest/",
    ) / _expected_file(release_name=release_name,extension=expected_extension)


def _run_deploy(
    require_saas_bucketfs_params,
    compression_strategy: CompressionStrategy,
    flavor_path: Path,
    release_name: str,
) -> dict[str, dict[str, DeployResult]]:
    saas_params = require_saas_bucketfs_params
    deploy_func = partial(
        api.deploy,
        flavor_path=(str(flavor_path),),
        release_name=release_name,
        compression_strategy=compression_strategy,
        # """ Added for Saas """
        saas_host=saas_params["url"],
        saas_account_id=saas_params["account_id"],
        saas_database_id=saas_params["database_id"],
        saas_pat=saas_params["pat"],
        path_in_bucket="saastest/",
    )
    return deploy_func()

def _validate_alter_session_cmd(
    expected_path_in_bucket: bfs.path.PathLike,
    deploy_result: DeployResult,
    release_name: str,
) -> None:
    complete_path_in_bucket = "/".join(
        [
            part
            for part in [
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

def _validate_human_readable_location(
    expected_path_in_bucket: bfs.path.PathLike,
    deploy_result: DeployResult,
) -> None:
    assert (
        deploy_result.human_readable_upload_location == f"Account id: {expected_path_in_bucket.bucket_api.account_id},Database id: {expected_path_in_bucket.bucket_api.database_id}, URL: {expected_path_in_bucket.bucket_api.url}, Path: {expected_path_in_bucket}"
    )

def validate_file_on_bucket_fs(
        expected_path_in_bucket: bfs.path.PathLike,
        compression_strategy: CompressionStrategy,
):
    expected_content = b"".join(expected_path_in_bucket.read())
    with TemporaryDirectory() as tmpdir:
        file_name = f'{tmpdir}/"slc.tar.gz"' if compression_strategy == CompressionStrategy.GZIP else f'{tmpdir}/"slc.tar"'
        with open(file_name, "wb") as file:
            file.write(expected_content)

        tar_mode = "r:gz" if compression_strategy == CompressionStrategy.GZIP else "r:"
        with tarfile.open(name=file_name, mode=tar_mode) as tf:  # type: ignore
            tf_members = tf.getmembers()
            last_tf_member = tf_members[-1]
            assert last_tf_member.name == "exasol-manifest.json"
            assert last_tf_member.path == "exasol-manifest.json"


def _validate_deploy(
    require_saas_bucketfs_params,
    compression_strategy: CompressionStrategy,
    expected_extension: str,
):
    release_name = "TEST"
    flavor_path = exaslct_utils.get_test_flavor()
    result = _run_deploy(
        require_saas_bucketfs_params,
        compression_strategy,
        flavor_path,
        release_name,
    )

    assert str(flavor_path) in result.keys()
    assert len(result) == 1
    assert str(flavor_path) in result.keys()
    assert len(result[str(flavor_path)]) == 1

    deploy_result = result[str(flavor_path)]["release"]
    assert f".build_output/cache/exports/test-flavor-release-" in deploy_result.release_path

    expected_path_in_bucket = _build_bfs_path(require_saas_bucketfs_params,release_name,expected_extension)
    assert (
        expected_path_in_bucket.as_udf_path()
        == deploy_result.bucket_path.as_udf_path()
    )
    # _validate_alter_session_cmd(
    #     expected_path_in_bucket,
    #     deploy_result,  release_name
    # )
    _validate_human_readable_location(expected_path_in_bucket,
                                      deploy_result, expected_extension, release_name
                                      )


    validate_file_on_bucket_fs(
        expected_path_in_bucket,
        compression_strategy=compression_strategy,
    )


def test_docker_api_deploy(require_saas_bucketfs_params):
    _validate_deploy(
        require_saas_bucketfs_params,
        compression_strategy=CompressionStrategy.GZIP,
        # path="test",
        expected_extension=".tar.gz",
    )

def test_docker_api_deploy_no_compression(require_saas_bucketfs_params):
    _validate_deploy(
        require_saas_bucketfs_params,
        compression_strategy=CompressionStrategy.NONE,
        path="test",
        expected_extension=".tar",
    )

def test_docker_api_deploy_without_path_in_bucket(require_saas_bucketfs_params):
    _validate_deploy(
        require_saas_bucketfs_params,
        compression_strategy=CompressionStrategy.GZIP,
        path=None,
        expected_extension=".tar.gz",
    )

def test_docker_api_deploy_fail_path_in_bucket(require_saas_bucketfs_params,):
    release_name = "TEST"
    saas_params = require_saas_bucketfs_params
    with pytest.raises(TaskRuntimeError):
        api.deploy(
            flavor_path=(str(exaslct_utils.get_test_flavor()),),
            release_name=release_name,

            saas_host=saas_params["url"],
            saas_account_id=saas_params["account_id"],
            saas_database_id=saas_params["database_id"],
            # saas_database_name=saas_params["database_name"],
            saas_pat=saas_params["pat"],
            path_in_bucket="saastest/",
        )

