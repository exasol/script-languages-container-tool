from pathlib import Path

from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import (
    DependencyLoggerBaseTask,
)


class CreateExportDirectory(DependencyLoggerBaseTask):
    # This task is needed because ExportContainerTask
    # requires the releases directory which stores the exported container.

    def run_task(self) -> None:
        export_directory = Path(self.get_cache_path(), "exports")
        export_directory.mkdir(parents=True, exist_ok=True)
        self.return_object(export_directory)
