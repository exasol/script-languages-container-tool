import luigi
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask


class SecurityScanParameter(DependencyLoggerBaseTask):
    release_goals = luigi.ListParameter(["release"])
