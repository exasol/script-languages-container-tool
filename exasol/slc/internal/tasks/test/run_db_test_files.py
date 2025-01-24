# pylint: disable=not-an-iterable
from typing import Any, Generator, Tuple

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
from exasol_integration_test_docker_environment.lib.data.environment_info import (
    EnvironmentInfo,
)

from exasol.slc.internal.tasks.test.run_db_test import RunDBTest
from exasol.slc.internal.tasks.test.run_db_tests_parameter import (
    ActualRunDBTestParameter,
    RunDBTestFilesParameter,
)
from exasol.slc.models.run_db_test_result import (
    RunDBTestCollectionResult,
    RunDBTestFilesResult,
    RunDBTestResult,
)


class RunDBTestFiles(
    FlavorBaseTask,
    RunDBTestFilesParameter,
    ActualRunDBTestParameter,
    DatabaseCredentialsParameter,
):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(self.flavor_path, str)
        assert isinstance(self.test_files, tuple)
        assert all(isinstance(x, str) for x in self.test_files)

        assert isinstance(self.languages, tuple)
        assert all(isinstance(x, str) for x in self.languages)

        assert isinstance(self.release_goal, str)
        assert isinstance(self.language_definition, str)
        assert isinstance(self.test_environment_info, EnvironmentInfo)
        assert isinstance(self.timeout, int)
        assert isinstance(self.no_cache, bool)
        assert isinstance(self.db_user, str)
        assert isinstance(self.db_password, str)
        assert isinstance(self.bucketfs_write_password, str)

    def extend_output_path(self) -> Tuple[str, ...]:
        return tuple(self.caller_output_path) + ("test_files",)

    def run_task(self) -> Generator[BaseTask, None, None]:
        results = []
        for language in self.languages:
            if language is not None:
                results_for_language = []
                for test_file in self.test_files:
                    test_result = yield from self.run_test(language, test_file)
                    results_for_language.append(test_result)
                results.append(
                    RunDBTestCollectionResult(
                        language=language, test_results=results_for_language
                    )
                )
        test_results = RunDBTestFilesResult(test_results=results)
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            test_results, 4
        )
        self.return_object(test_results)

    def run_test(
        self, language: str, test_file: str
    ) -> Generator[BaseTask, Any, RunDBTestResult]:
        #
        # Correct return type is Generator[RunDBTestsInDirectory, Any, List[RunDBTestResult]]
        # TODO: Fix after https://github.com/exasol/integration-test-docker-environment/issues/445
        #

        task = self.create_child_task_with_common_params(
            RunDBTest,
            test_file=test_file,
            language=language,
        )
        test_result_future = yield from self.run_dependencies(task)
        test_result = self.get_values_from_future(test_result_future)
        assert isinstance(test_result, RunDBTestResult)
        return test_result
