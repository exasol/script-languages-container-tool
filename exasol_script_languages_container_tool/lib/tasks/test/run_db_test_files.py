from typing import Any, Generator

from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorBaseTask
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import JsonPickleTarget
from exasol_integration_test_docker_environment.lib.data.database_credentials import DatabaseCredentialsParameter

from exasol_script_languages_container_tool.lib.tasks.test.run_db_test import RunDBTest
from exasol_script_languages_container_tool.lib.tasks.test.run_db_test_in_directory import RunDBTestsInDirectory
from exasol_script_languages_container_tool.lib.tasks.test.run_db_test_result import RunDBTestCollectionResult, \
    RunDBTestFilesResult, \
    RunDBTestResult
from exasol_script_languages_container_tool.lib.tasks.test.run_db_tests_parameter import RunDBTestFilesParameter, \
    ActualRunDBTestParameter


class RunDBTestFiles(FlavorBaseTask,
                     RunDBTestFilesParameter,
                     ActualRunDBTestParameter,
                     DatabaseCredentialsParameter):

    def extend_output_path(self):
        return self.caller_output_path + ("test_files",)

    def run_task(self):
        results = []
        for language in self.languages:
            results_for_language = []
            for test_file in self.test_files:
                test_result = yield from self.run_test(language, test_file)
                results_for_language.append(test_result)
            results.append(RunDBTestCollectionResult(language=language,
                                                     test_results=results_for_language))
        test_results = RunDBTestFilesResult(test_results=results)
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(test_results, 4)
        self.return_object(test_results)

    def run_test(self, language: str, test_file: str) -> \
            Generator[RunDBTestsInDirectory, Any, RunDBTestResult]:
        task = self.create_child_task_with_common_params(
            RunDBTest,
            test_file=test_file,
            language=language,
        )
        test_result_future = yield from self.run_dependencies(task)
        test_result = self.get_values_from_future(test_result_future)
        return test_result
