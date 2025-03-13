from typing import Any, Generator

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import (
    JsonPickleTarget,
)
from exasol_integration_test_docker_environment.lib.models.data.database_credentials import (
    DatabaseCredentialsParameter,
)

from exasol.slc.internal.tasks.test.run_db_generic_language_tests import (
    RunDBGenericLanguageTest,
)
from exasol.slc.internal.tasks.test.run_db_test_files import RunDBTestFiles
from exasol.slc.internal.tasks.test.run_db_test_folder import RunDBTestFolder
from exasol.slc.internal.tasks.test.run_db_tests_parameter import (
    ActualRunDBTestParameter,
    RunDBTestsInTestConfigParameter,
)
from exasol.slc.models.run_db_test_result import (
    RunDBTestFilesResult,
    RunDBTestFoldersResult,
    RunDBTestsInTestConfigResult,
)


class RunDBTestsInTestConfig(
    FlavorBaseTask,
    RunDBTestsInTestConfigParameter,
    ActualRunDBTestParameter,
    DatabaseCredentialsParameter,
):
    # TODO fetch database logs after test execution

    def run_task(self) -> Generator[BaseTask, None, None]:
        test_folders_output = yield from self.run_test_folder()
        test_files_output = yield from self.run_test_files()
        generic_language_test_output = yield from self.run_generic_language_test()
        flavor_path: str = self.flavor_path  # type: ignore
        result = RunDBTestsInTestConfigResult(
            flavor_path=flavor_path,
            release_goal=self.release_goal,
            generic_language_tests_output=generic_language_test_output,
            test_folders_output=test_folders_output,
            test_files_output=test_files_output,
        )
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            result, 4
        )
        self.return_object(result)

    def run_generic_language_test(
        self,
    ) -> Generator[BaseTask, Any, RunDBTestFoldersResult]:
        #
        # Correct return type is Generator[RunDBGenericLanguageTest, Any, RunDBTestFilesResult]
        # TODO: Fix after https://github.com/exasol/integration-test-docker-environment/issues/445
        #
        generic_language_test_task = self.create_child_task_with_common_params(
            RunDBGenericLanguageTest
        )
        generic_language_test_output_future = yield from self.run_dependencies(
            generic_language_test_task
        )
        run_db_test_folder_result = self.get_values_from_future(
            generic_language_test_output_future
        )
        assert isinstance(run_db_test_folder_result, RunDBTestFoldersResult)
        return run_db_test_folder_result

    def run_test_files(
        self,
    ) -> Generator[BaseTask, Any, RunDBTestFilesResult]:
        #
        # Correct return type is Generator[RunDBGenericLanguageTest, Any, RunDBTestFilesResult]
        # TODO: Fix after https://github.com/exasol/integration-test-docker-environment/issues/445
        #
        test_files_task = self.create_child_task_with_common_params(RunDBTestFiles)
        test_files_output_future = yield from self.run_dependencies(test_files_task)
        run_db_test_file_result = self.get_values_from_future(test_files_output_future)
        assert isinstance(run_db_test_file_result, RunDBTestFilesResult)
        return run_db_test_file_result

    def run_test_folder(
        self,
    ) -> Generator[BaseTask, Any, RunDBTestFoldersResult]:
        #
        # Correct return type is Generator[RunDBGenericLanguageTest, Any, RunDBTestFilesResult]
        # TODO: Fix after https://github.com/exasol/integration-test-docker-environment/issues/445
        #
        test_folder_task = self.create_child_task_with_common_params(RunDBTestFolder)
        test_folder_output_future = yield from self.run_dependencies(test_folder_task)
        run_db_test_folder_result = self.get_values_from_future(
            test_folder_output_future
        )
        assert isinstance(run_db_test_folder_result, RunDBTestFoldersResult)
        return run_db_test_folder_result
