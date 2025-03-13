from typing import Any, Generator, List, Tuple

import luigi
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

from exasol.slc.internal.tasks.test.run_db_test import RunDBTest
from exasol.slc.internal.tasks.test.run_db_tests_parameter import RunDBTestParameter
from exasol.slc.models.run_db_test_result import (
    RunDBTestDirectoryResult,
    RunDBTestResult,
)


class RunDBTestsInDirectory(
    FlavorBaseTask, RunDBTestParameter, DatabaseCredentialsParameter
):
    directory: str = luigi.Parameter()  # type: ignore

    def extend_output_path(self) -> Tuple[str, ...]:
        return tuple(self.caller_output_path) + (self.directory,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._test_container_info = (
            self.test_environment_info.test_container_info  # pylint: disable=no-member
        )  # pylint: disable=no-member
        self.tasks = self.create_test_tasks_from_directory(self.directory)

    def run_task(self) -> Generator[BaseTask, None, None]:
        test_results = yield from self.run_tests()
        result = RunDBTestDirectoryResult(
            test_results=test_results,
            language=self.language if self.language is not None else "",
            test_folder=self.directory,
        )
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            test_results, 4
        )
        self.return_object(result)

    def run_tests(self) -> Generator[BaseTask, Any, List[RunDBTestResult]]:
        #
        # Correct return type is Generator[RunDBTest, Any, List[RunDBTestResult]]
        # TODO: Fix after https://github.com/exasol/integration-test-docker-environment/issues/445
        #
        test_results = []
        for test_task_config in self.tasks:
            test_result_future = yield from self.run_dependencies(test_task_config)
            test_result = self.get_values_from_future(test_result_future)
            assert isinstance(test_result, RunDBTestResult)
            test_results.append(test_result)
        return test_results

    def create_test_tasks_from_directory(self, directory: str) -> List[RunDBTest]:
        assert self._test_container_info is not None
        with self._get_docker_client() as docker_client:
            test_container = docker_client.containers.get(
                self._test_container_info.container_name
            )
            exit_code, ls_output = test_container.exec_run(
                cmd="ls /tests/test/%s/" % directory
            )
            test_files = ls_output.decode("utf-8").split("\n")
            tasks = [
                self.create_test_task(directory, test_file)
                for test_file in test_files
                if test_file != "" and test_file.endswith(".py")
            ]
            return tasks

    def create_test_task(self, directory: str, test_file: str) -> RunDBTest:
        task = self.create_child_task_with_common_params(
            RunDBTest, test_file=directory + "/" + test_file
        )
        return task
