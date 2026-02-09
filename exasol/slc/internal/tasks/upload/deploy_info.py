from dataclasses import dataclass

import exasol.bucketfs as bfs  # type: ignore

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
    bucketfs_host: str | None,
    bucketfs_port: int | None,
    bucket_name: str | None,
    bucketfs_name: str | None,
    bucketfs_username: str | None,
    bucketfs_password: str | None,
    ssl_cert_path: str | None,
    use_ssl_cert_validation: bool,
    path_in_bucket: str | None,
    saas_token: str | None,
    saas_database_id: str | None,
    saas_database_name: str | None,
    saas_account_id: str | None,
    saas_url: str | None,
) -> DeployResult:
    complete_release_name = deploy_info.complete_release_name
    bucket_path = (
        bfs.path.infer_path(
            bucketfs_host=bucketfs_host,
            bucketfs_port=bucketfs_port,
            bucket=bucket_name,
            bucketfs_name=bucketfs_name,
            bucketfs_user=bucketfs_username,
            bucketfs_password=bucketfs_password,
            bucketfs_use_https=bucketfs_use_https,
            use_ssl_cert_validation=use_ssl_cert_validation,
            ssl_trusted_ca=ssl_cert_path,
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
