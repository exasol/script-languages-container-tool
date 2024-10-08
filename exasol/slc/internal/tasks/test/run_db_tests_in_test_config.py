from typing import Any, Generator

from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import (
    JsonPickleTarget,
)
from exasol_integration_test_docker_environment.lib.data.database_credentials import (
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

    def run_task(self):
        test_folders_output = yield from self.run_test_folder()
        test_files_output = yield from self.run_test_files()
        generic_language_test_output = yield from self.run_generic_language_test()
        result = RunDBTestsInTestConfigResult(
            flavor_path=self.flavor_path,
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
    ) -> Generator[RunDBGenericLanguageTest, Any, RunDBTestFoldersResult]:
        generic_language_test_task = self.create_child_task_with_common_params(
            RunDBGenericLanguageTest
        )
        generic_language_test_output_future = yield from self.run_dependencies(
            generic_language_test_task
        )
        return self.get_values_from_future(generic_language_test_output_future)

    def run_test_files(
        self,
    ) -> Generator[RunDBGenericLanguageTest, Any, RunDBTestFilesResult]:
        test_files_task = self.create_child_task_with_common_params(RunDBTestFiles)
        test_files_output_future = yield from self.run_dependencies(test_files_task)
        return self.get_values_from_future(test_files_output_future)

    def run_test_folder(
        self,
    ) -> Generator[RunDBGenericLanguageTest, Any, RunDBTestFoldersResult]:
        test_folder_task = self.create_child_task_with_common_params(RunDBTestFolder)
        test_folder_output_future = yield from self.run_dependencies(test_folder_task)
        return self.get_values_from_future(test_folder_output_future)
