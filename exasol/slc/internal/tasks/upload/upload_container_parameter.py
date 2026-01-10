from typing import Optional

import luigi

from exasol.slc.internal.tasks.export.export_container_parameters import (
    ExportContainerOptionsParameter,
)


class UploadContainerParameter(ExportContainerOptionsParameter):
    database_host: str = luigi.OptionalParameter(None)  # type: ignore
    bucketfs_port: int = luigi.IntParameter(-1)  # type: ignore
    bucketfs_username: str = luigi.OptionalParameter(None, significant=False)  # type: ignore
    bucketfs_password: str = luigi.OptionalParameter(
        None, significant=False, visibility=luigi.parameter.ParameterVisibility.HIDDEN
    )  # type: ignore
    bucketfs_name: str = luigi.OptionalParameter(None)  # type: ignore
    bucket_name: str = luigi.OptionalParameter(None)  # type: ignore
    path_in_bucket: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    bucketfs_https: bool = luigi.BoolParameter(False)  # type: ignore
    release_name: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    ssl_cert_path: str = luigi.OptionalParameter(None)  # type: ignore
    use_ssl_cert_validation: bool = luigi.BoolParameter(True)  # type: ignore
    saas_host: str = luigi.OptionalParameter(None)  # type: ignore
    saas_pat: str = luigi.OptionalParameter(None)  # type: ignore
    saas_account_id: str = luigi.OptionalParameter(None)  # type: ignore
    saas_database_id: str = luigi.OptionalParameter(None)  # type: ignore
    saas_database_name: str = luigi.OptionalParameter(None)  # type: ignore
