from pathlib import Path
from typing import Dict, Optional, TextIO, Tuple

import luigi
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import (
    JsonPickleTarget,
)
from exasol_integration_test_docker_environment.lib.test_environment.parameter.spawn_test_environment_parameter import (
    SpawnTestEnvironmentParameter,
)

from exasol.slc.internal.tasks.test.run_db_tests_parameter import (
    GeneralRunDBTestParameter,
    RunDBTestsInTestConfigParameter,
)
from exasol.slc.internal.tasks.test.test_runner_db_test_task import TestRunnerDBTestTask
from exasol.slc.models.run_db_test_result import RunDBTestsInTestConfigResult
from exasol.slc.models.test_result import AllTestsResult, FlavorTestResult

STATUS_INDENT = 2


class TestContainerParameter(
    RunDBTestsInTestConfigParameter, GeneralRunDBTestParameter
):
    release_goals: Tuple[str, ...] = luigi.ListParameter(["release"])  # type: ignore
    languages: Tuple[Optional[str], ...] = luigi.ListParameter([None])  # type: ignore
    reuse_uploaded_container: bool = luigi.BoolParameter(False, significant=False)  # type: ignore


class TestStatusPrinter:
    def __init__(self, file: TextIO) -> None:
        self.file = file

    def print_status_for_all_tests(
        self, test_results: Dict[str, FlavorTestResult]
    ) -> None:
        for flavor, test_result_of_flavor in test_results.items():
            print(
                f"- Tests: {self.get_status_string(test_result_of_flavor.tests_are_ok)}",
                file=self.file,
            )
            self.print_status_for_flavor(
                flavor, test_result_of_flavor, indent=STATUS_INDENT
            )

    def print_status_for_flavor(
        self, flavor_path: str, test_result_of_flavor: FlavorTestResult, indent: int
    ) -> None:
        print(
            self.get_indent_str(indent)
            + f"- Tests for flavor {flavor_path}: {self.get_status_string(test_result_of_flavor.tests_are_ok)}",
            file=self.file,
        )
        for (
            release_goal,
            test_results_of_release_goal,
        ) in test_result_of_flavor.test_results_per_release_goal.items():
            self.print_status_for_release_goal(
                release_goal,
                test_results_of_release_goal,
                indent=indent + STATUS_INDENT,
            )

    def print_status_for_release_goal(
        self,
        release_goal: str,
        test_results_of_release_goal: RunDBTestsInTestConfigResult,
        indent: int,
    ) -> None:
        print(
            self.get_indent_str(indent)
            + f"- Tests for release goal {release_goal}: "
            + self.get_status_string(test_results_of_release_goal.tests_are_ok),
            file=self.file,
        )
        self.print_status_for_generic_language_tests(
            test_results_of_release_goal, indent=indent + STATUS_INDENT
        )
        self.print_status_for_test_folders(
            test_results_of_release_goal, indent=indent + STATUS_INDENT
        )
        self.print_status_for_test_files(
            test_results_of_release_goal, indent=indent + STATUS_INDENT
        )

    def print_status_for_test_files(
        self, test_result_of_flavor: RunDBTestsInTestConfigResult, indent: int
    ) -> None:
        for (
            test_results_for_test_files
        ) in test_result_of_flavor.test_files_output.test_results:
            print(
                self.get_indent_str(indent) + f"- Tests in test files "
                f"with language {test_results_for_test_files.language}: "
                f"{self.get_status_string(test_results_for_test_files.tests_are_ok)}",
                file=self.file,
            )

    def print_status_for_test_folders(
        self, test_result_of_flavor: RunDBTestsInTestConfigResult, indent: int
    ) -> None:
        for (
            test_results_for_test_folder
        ) in test_result_of_flavor.test_folders_output.test_results:
            print(
                self.get_indent_str(indent)
                + f"- Tests in test folder {test_results_for_test_folder.test_folder} "
                f"with language {test_results_for_test_folder.test_folder}: "
                f"{self.get_status_string(test_results_for_test_folder.tests_are_ok)}",
                file=self.file,
            )

    def print_status_for_generic_language_tests(
        self, test_result_of_flavor: RunDBTestsInTestConfigResult, indent: int
    ) -> None:
        for (
            test_results_for_test_folder
        ) in test_result_of_flavor.generic_language_tests_output.test_results:
            print(
                self.get_indent_str(indent)
                + f"- Tests in test folder {test_results_for_test_folder.test_folder}"
                f"with language {test_results_for_test_folder.language}: "
                f"{self.get_status_string(test_results_for_test_folder.tests_are_ok)}",
                file=self.file,
            )

    @staticmethod
    def get_indent_str(indent: int) -> str:
        return " " * indent

    @staticmethod
    def get_status_string(status: bool) -> str:
        return "OK" if status else "FAILED"


class TestContainer(
    FlavorsBaseTask, TestContainerParameter, SpawnTestEnvironmentParameter
):
    def __init__(self, *args, **kwargs) -> None:
        self.test_results_futures = None
        super().__init__(*args, **kwargs)
        command_line_output_path = self.get_output_path().joinpath(
            "command_line_output"
        )
        self.command_line_output_target = luigi.LocalTarget(
            str(command_line_output_path)
        )

    def register_required(self) -> None:
        tasks: Dict[str, TestFlavorContainer] = self.create_tasks_for_flavors_with_common_params(  # type: ignore
            TestFlavorContainer
        )  # type: ignore
        self.test_results_futures = self.register_dependencies(tasks)

    def run_task(self) -> None:
        test_results: Dict[str, FlavorTestResult] = self.get_values_from_futures(
            self.test_results_futures
        )
        assert isinstance(test_results, dict)
        assert all(isinstance(x, str) for x in test_results.keys())
        assert all(isinstance(x, FlavorTestResult) for x in test_results.values())

        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            test_results, 4
        )

        with self.command_line_output_target.open("w") as file:
            TestStatusPrinter(file).print_status_for_all_tests(test_results)

        test_result = AllTestsResult(
            test_results_per_flavor=test_results,
            command_line_output_path=Path(self.command_line_output_target.path),
        )
        self.return_object(test_result)


class TestFlavorContainer(
    FlavorBaseTask, TestContainerParameter, SpawnTestEnvironmentParameter
):

    def __init__(self, *args, **kwargs) -> None:
        self.test_result_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        tasks = {
            release_goal: self.generate_tasks_for_flavor(release_goal)
            for release_goal in self.release_goals  # type: ignore  # pylint: disable=not-an-iterable
        }
        self.test_result_futures = self.register_dependencies(tasks)

    def generate_tasks_for_flavor(self, release_goal: str) -> TestRunnerDBTestTask:
        task = self.create_child_task_with_common_params(
            TestRunnerDBTestTask, release_goal=release_goal
        )
        return task

    def run_task(self) -> None:
        test_results: Dict[str, RunDBTestsInTestConfigResult] = (
            self.get_values_from_futures(self.test_result_futures)
        )
        assert isinstance(test_results, dict)
        assert all(isinstance(x, str) for x in test_results.keys())
        assert all(
            isinstance(x, RunDBTestsInTestConfigResult) for x in test_results.values()
        )

        flavor_path: str = self.flavor_path  # type: ignore
        result = FlavorTestResult(flavor_path, test_results)
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(
            test_results, 4
        )
        self.return_object(result)
