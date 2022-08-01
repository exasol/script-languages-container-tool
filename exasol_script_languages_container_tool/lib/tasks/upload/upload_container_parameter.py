import luigi
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask


class UploadContainerParameter:
    database_host = luigi.Parameter()
    bucketfs_port = luigi.IntParameter()
    bucketfs_username = luigi.Parameter(significant=False)
    bucketfs_password = luigi.Parameter(significant=False, visibility=luigi.parameter.ParameterVisibility.HIDDEN)
    bucketfs_name = luigi.Parameter()
    bucket_name = luigi.Parameter()
    path_in_bucket = luigi.OptionalParameter()
    bucketfs_https = luigi.BoolParameter(False)
    release_name = luigi.OptionalParameter()
