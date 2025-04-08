from typing import Optional

import luigi

from exasol.slc.internal.tasks.export.export_container_parameters import (
    ExportContainerOptionsParameter,
)


class UploadContainerParameter(ExportContainerOptionsParameter):
    database_host: str = luigi.Parameter()  # type: ignore
    bucketfs_port: int = luigi.IntParameter()  # type: ignore
    bucketfs_username: str = luigi.Parameter(significant=False)  # type: ignore
    bucketfs_password: str = luigi.Parameter(
        significant=False, visibility=luigi.parameter.ParameterVisibility.HIDDEN
    )  # type: ignore
    bucketfs_name: str = luigi.Parameter()  # type: ignore
    bucket_name: str = luigi.Parameter()  # type: ignore
    path_in_bucket: Optional[str] = luigi.OptionalParameter()  # type: ignore
    bucketfs_https: bool = luigi.BoolParameter(False)  # type: ignore
    release_name: Optional[str] = luigi.OptionalParameter()  # type: ignore
    ssl_cert_path: str = luigi.Parameter()  # type: ignore
    use_ssl_cert_validation: bool = luigi.BoolParameter(True)  # type: ignore
