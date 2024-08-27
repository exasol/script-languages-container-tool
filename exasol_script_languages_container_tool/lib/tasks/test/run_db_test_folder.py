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

from exasol_script_languages_container_tool.lib.tasks.test.run_db_test_in_directory import (
    RunDBTestsInDirectory,
)
from exasol_script_languages_container_tool.lib.tasks.test.run_db_test_result import (
    RunDBTestDirectoryResult,
    RunDBTestFoldersResult,
)
from exasol_script_languages_container_tool.lib.tasks.test.run_db_tests_parameter import (
    ActualRunDBTestParameter,
    RunDBTestFolderParameter,
)


class RunDBTestFolder(
    FlavorBaseTask,
    RunDBTestFolderParameter,
    ActualRunDBTestParameter,
    DatabaseCredentialsParameter,
):

    def extend_output_path(self):
        return self.caller_output_path + ("test_folder",)

    def run_task(self):
        results = []
        for language in self.languages:  # pylint: disable=not-an-iterable
            for test_folder in self.test_folders:  # pylint: disable=not-an-iterable
                test_result = yield from self.run_test(language, test_folder)
                results.append(test_result)
        self.return_object(RunDBTestFoldersResult(test_results=results))

    def run_test(
        self, language: str, test_folder: str
    ) -> Generator[RunDBTestsInDirectory, Any, RunDBTestDirectoryResult]:
        task = self.create_child_task_with_common_params(
            RunDBTestsInDirectory,
            language=language,
            directory=test_folder,
        )
        test_result_future = yield from self.run_dependencies(task)
        test_result = self.get_values_from_future(
            test_result_future
        )  # type: RunDBTestDirectoryResult
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            test_result, 4
        )
        return test_result
