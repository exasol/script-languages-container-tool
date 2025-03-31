from typing import Dict, Generator

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.models.data.database_credentials import (
    DatabaseCredentials,
)
from exasol_integration_test_docker_environment.lib.models.data.environment_info import (
    EnvironmentInfo,
)

from exasol.slc.internal.tasks.export.export_containers import ExportFlavorContainer
from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    TestRunnerDBTestBaseTask,
)
from exasol.slc.internal.tasks.test.upload_exported_container import (
    UploadExportedContainer,
)
from exasol.slc.models.export_info import ExportInfo


class TestRunnerDBTestWithExportTask(TestRunnerDBTestBaseTask):

    def register_required(self) -> None:
        self.register_export_container()
        self.register_spawn_test_environment()

    def register_export_container(self) -> None:
        export_container_task = self.create_child_task(
            ExportFlavorContainer,
            release_goals=[self.release_goal],
            flavor_path=self.flavor_path,
        )
        self._export_infos_future = self.register_dependency(export_container_task)

    def run_task(self) -> Generator[BaseTask, None, None]:
        export_infos: Dict[str, ExportInfo] = self.get_values_from_future(
            self._export_infos_future
        )  # type: ignore
        assert isinstance(export_infos, dict)
        assert all(isinstance(x, str) for x in export_infos.keys())
        assert all(isinstance(x, ExportInfo) for x in export_infos.values())

        export_info = export_infos[self.release_goal]
        self.test_environment_info = self.get_values_from_future(
            self._test_environment_info_future
        )  # type: ignore
        assert isinstance(self.test_environment_info, EnvironmentInfo)

        database_credentials = self.get_database_credentials()
        yield from self.upload_container(database_credentials, export_info)
        yield from self.populate_test_engine_data(
            self.test_environment_info, database_credentials
        )
        test_results = yield from self.run_test(
            self.test_environment_info, export_info.name
        )
        self.return_object(test_results)

    def upload_container(
        self, database_credentials: DatabaseCredentials, export_info: ExportInfo
    ) -> Generator[UploadExportedContainer, None, None]:
        reuse = (
            self.reuse_database
            and self.reuse_uploaded_container
            and not export_info.is_new
        )
        assert self.test_environment_info is not None
        upload_task = self.create_child_task_with_common_params(
            UploadExportedContainer,
            file_to_upload=export_info.cache_file,
            target_name=export_info.name,
            environment_name=self.test_environment_info.name,
            test_environment_info=self.test_environment_info,
            reuse_uploaded=reuse,
            bucketfs_write_password=database_credentials.bucketfs_write_password,
            executor_factory=self._executor_factory(
                self.test_environment_info.database_info
            ),
        )
        yield from self.run_dependencies(upload_task)
