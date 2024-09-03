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
) -> DeployResult:
    backend = bfs.path.StorageBackend.onprem
    verify = ssl_cert_path or use_ssl_cert_validation

    complete_release_name = deploy_info.complete_release_name

    url_prefix = "https://" if bucketfs_use_https else "http://"
    url = f"{url_prefix}{bucketfs_host}:{bucketfs_port}"
    bucket_path = (
        bfs.path.build_path(
            backend=backend,
            url=url,
            bucket_name=bucket_name,
            service_name=bucketfs_name,
            username=bucketfs_username,
            password=bucketfs_password,
            verify=verify,
            path=path_in_bucket or "",
        )
        / f"{complete_release_name}.tar.gz"
    )

    return DeployResult(
        release_path=deploy_info.release_path,
        human_readable_upload_location=deploy_info.human_readable_location,
        bucket_path=bucket_path,
        language_definition_builder=deploy_info.language_definition_builder,
    )
