import luigi


class UploadContainerParameter:
    database_host = luigi.Parameter()
    bucketfs_port = luigi.IntParameter()
    bucketfs_username = luigi.Parameter(significant=False)
    bucketfs_password = luigi.Parameter(
        significant=False, visibility=luigi.parameter.ParameterVisibility.HIDDEN
    )
    bucketfs_name = luigi.Parameter()
    bucket_name = luigi.Parameter()
    path_in_bucket = luigi.OptionalParameter()
    bucketfs_https = luigi.BoolParameter(False)
    release_name = luigi.OptionalParameter()
    ssl_cert_path = luigi.Parameter()
    use_ssl_cert_validation = luigi.BoolParameter(True)
