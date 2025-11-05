from dataclasses import dataclass

import exasol.bucketfs as bfs  # type: ignore
from exasol.bucketfs import SaaSBucket
from exasol.bucketfs._path import StorageBackend

from exasol.slc.internal.utils.file_utilities import detect_container_file_extension
from exasol.slc.models.deploy_result import DeployResult
from exasol.slc.models.language_definitions_builder import LanguageDefinitionsBuilder


@dataclass
class DeployInfo:
    release_path: str
    complete_release_name: str
    human_readable_location: str
    language_definition_builder: LanguageDefinitionsBuilder
    file_extension: str


def toDeployResult(
    deploy_info: DeployInfo,
    bucketfs_use_https: bool,
    bucketfs_host: str,
    bucketfs_port: int,
    bucket_name: str,
    bucketfs_name: str,
    bucketfs_username: str,
    bucketfs_password: str,
    ssl_cert_path: str,
    use_ssl_cert_validation: bool,
    path_in_bucket: str,
    saas_token: str,
    saas_database_id: str,
    saas_database_name: str,
    saas_account_id: str,
    saas_url: str,
) -> DeployResult:
    verify = ssl_cert_path or use_ssl_cert_validation

    complete_release_name = deploy_info.complete_release_name

    url_prefix = "https://" if bucketfs_use_https else "http://"
    url = f"{url_prefix}{bucketfs_host}:{bucketfs_port}"
    bucket_path = (
        bfs.path.infer_path(
            bucketfs_host=url,
            bucket=bucket_name,
            bucketfs_name=bucketfs_name,
            bucketfs_user=bucketfs_username,
            bucketfs_password=bucketfs_password,
            use_ssl_cert_validation=verify,
            path_in_bucket=path_in_bucket or "",
            saas_url=saas_url,
            saas_token=saas_token,
            saas_database_id=saas_database_id,
            saas_account_id=saas_account_id,
            saas_database_name=saas_database_name,
        )
        / f"{complete_release_name}{deploy_info.file_extension}"
    )

    return DeployResult(
        release_path=deploy_info.release_path,
        human_readable_upload_location=deploy_info.human_readable_location,
        bucket_path=bucket_path,
        language_definition_builder=deploy_info.language_definition_builder,
    )
