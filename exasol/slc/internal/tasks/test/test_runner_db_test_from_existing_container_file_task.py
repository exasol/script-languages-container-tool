from typing import Generator

import luigi
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.models.data.database_credentials import (
    DatabaseCredentials,
)
from exasol_integration_test_docker_environment.lib.models.data.environment_info import (
    EnvironmentInfo,
)

from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    TestRunnerDBTestBaseTask,
)
from exasol.slc.internal.tasks.test.upload_exported_container import (
    UploadExportedContainer,
)


class TestRunnerDBTestFromExistingContainerFileTask(TestRunnerDBTestBaseTask):
    use_existing_container: str = luigi.OptionalParameter()  # type: ignore

    def register_required(self) -> None:
        self.register_spawn_test_environment()

    def run_task(self) -> Generator[BaseTask, None, None]:
        self.test_environment_info = self.get_values_from_future(
            self._test_environment_info_future
        )  # type: ignore
        assert isinstance(self.test_environment_info, EnvironmentInfo)

        database_credentials = self.get_database_credentials()
        target_name = self.get_flavor_name()
        yield from self.upload_container(database_credentials, target_name)
        yield from self.populate_test_engine_data(
            self.test_environment_info, database_credentials
        )
        test_results = yield from self.run_test(self.test_environment_info, target_name)
        self.return_object(test_results)

    def upload_container(
        self, database_credentials: DatabaseCredentials, target_name: str
    ) -> Generator[UploadExportedContainer, None, None]:
        reuse = self.reuse_database and self.reuse_uploaded_container
        assert self.test_environment_info is not None
        upload_task = self.create_child_task_with_common_params(
            UploadExportedContainer,
            file_to_upload=self.use_existing_container,
            target_name=target_name,
            environment_name=self.test_environment_info.name,
            test_environment_info=self.test_environment_info,
            reuse_uploaded=reuse,
            bucketfs_write_password=database_credentials.bucketfs_write_password,
            executor_factory=self._executor_factory(
                self.test_environment_info.database_info
            ),
        )
        yield from self.run_dependencies(upload_task)
