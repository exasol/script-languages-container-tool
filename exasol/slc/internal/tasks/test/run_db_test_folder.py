from typing import Any, Generator, Optional, Tuple

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import (
    JsonPickleTarget,
)
from exasol_integration_test_docker_environment.lib.data.database_credentials import (
    DatabaseCredentialsParameter,
)

from exasol.slc.internal.tasks.test.run_db_test_in_directory import (
    RunDBTestsInDirectory,
)
from exasol.slc.internal.tasks.test.run_db_tests_parameter import (
    ActualRunDBTestParameter,
    RunDBTestFolderParameter,
)
from exasol.slc.models.run_db_test_result import (
    RunDBTestDirectoryResult,
    RunDBTestFoldersResult,
)


class RunDBTestFolder(
    FlavorBaseTask,
    RunDBTestFolderParameter,
    ActualRunDBTestParameter,
    DatabaseCredentialsParameter,
):

    def extend_output_path(self) -> Tuple[str, ...]:
        return tuple(self.caller_output_path) + ("test_folder",)

    def run_task(self) -> Generator[BaseTask, None, None]:
        results = []
        for language in self.languages:  # pylint: disable=not-an-iterable
            for test_folder in self.test_folders:  # pylint: disable=not-an-iterable
                test_result = yield from self.run_test(language, test_folder)
                results.append(test_result)
        self.return_object(RunDBTestFoldersResult(test_results=results))

    def run_test(
        self, language: Optional[str], test_folder: str
    ) -> Generator[BaseTask, Any, RunDBTestDirectoryResult]:
        #
        # Correct return type is Generator[RunDBTestsInDirectory, Any, List[RunDBTestResult]]
        # TODO: Fix after https://github.com/exasol/integration-test-docker-environment/issues/445
        #
        task = self.create_child_task_with_common_params(
            RunDBTestsInDirectory,
            language=language,
            directory=test_folder,
        )
        test_result_future = yield from self.run_dependencies(task)
        test_result = self.get_values_from_future(test_result_future)
        assert isinstance(test_result, RunDBTestDirectoryResult)
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            test_result, 4
        )
        return test_result
