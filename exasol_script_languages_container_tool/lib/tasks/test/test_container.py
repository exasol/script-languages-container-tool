from pathlib import Path
from typing import Dict

import luigi
from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorsBaseTask, FlavorBaseTask
from exasol_integration_test_docker_environment.lib.base.info import Info
from exasol_integration_test_docker_environment.lib.base.json_pickle_target import JsonPickleTarget
from exasol_integration_test_docker_environment.lib.test_environment.parameter.spawn_test_environment_parameter import \
    SpawnTestEnvironmentParameter

from exasol_script_languages_container_tool.lib.tasks.test.run_db_test_result import RunDBTestsInTestConfigResult
from exasol_script_languages_container_tool.lib.tasks.test.run_db_tests_parameter import \
    RunDBTestsInTestConfigParameter, \
    GeneralRunDBTestParameter
from exasol_script_languages_container_tool.lib.tasks.test.test_runner_db_test_task import TestRunnerDBTestTask

STATUS_INDENT = 2


class TestContainerParameter(RunDBTestsInTestConfigParameter,
                             GeneralRunDBTestParameter):
    release_goals = luigi.ListParameter(["release"])
    languages = luigi.ListParameter([None])
    reuse_uploaded_container = luigi.BoolParameter(False, significant=False)


class FlavorTestResult:
    def __init__(self, flavor_path: str, test_results_per_release_goal: Dict[str, RunDBTestsInTestConfigResult]):
        self.flavor_path = str(flavor_path)
        self.test_results_per_release_goal = test_results_per_release_goal
        self.tests_are_ok = all(test_result.tests_are_ok
                                for test_result
                                in test_results_per_release_goal.values())


class AllTestsResult(Info):
    def __init__(self, test_results_per_flavor: Dict[str, FlavorTestResult], command_line_output_path: Path):
        self.test_results_per_flavor = test_results_per_flavor
        self.tests_are_ok = all(test_result.tests_are_ok
                                for test_result
                                in test_results_per_flavor.values())
        self.command_line_output_path = command_line_output_path


class TestStatusPrinter:
    def __init__(self, file):
        self.file = file

    def print_status_for_all_tests(self, test_results: Dict[str,FlavorTestResult]):
        for flavor, test_result_of_flavor in test_results.items():
            print(f"- Tests: {self.get_status_string(test_result_of_flavor.tests_are_ok)}",
                  file=self.file)
            self.print_status_for_flavor(flavor, test_result_of_flavor, indent=STATUS_INDENT)

    def print_status_for_flavor(self,
                                flavor_path: str,
                                test_result_of_flavor: FlavorTestResult,
                                indent: int):
        print(self.get_indent_str(indent) +
              f"- Tests for flavor {flavor_path}: {self.get_status_string(test_result_of_flavor.tests_are_ok)}",
              file=self.file)
        for release_goal, test_results_of_release_goal \
                in test_result_of_flavor.test_results_per_release_goal.items():
            self.print_status_for_release_goal(release_goal, test_results_of_release_goal,
                                               indent=indent + STATUS_INDENT)

    def print_status_for_release_goal(self,
                                      release_goal: str,
                                      test_results_of_release_goal: RunDBTestsInTestConfigResult,
                                      indent: int):
        print(self.get_indent_str(indent) +
              f"- Tests for release goal {release_goal}: " +
              self.get_status_string(test_results_of_release_goal.tests_are_ok),
              file=self.file)
        self.print_status_for_generic_language_tests(test_results_of_release_goal, indent=indent + STATUS_INDENT)
        self.print_status_for_test_folders(test_results_of_release_goal, indent=indent + STATUS_INDENT)
        self.print_status_for_test_files(test_results_of_release_goal, indent=indent + STATUS_INDENT)

    def print_status_for_test_files(self,
                                    test_result_of_flavor: RunDBTestsInTestConfigResult,
                                    indent: int):
        for test_results_for_test_files in test_result_of_flavor.test_files_output.test_results:
            print(self.get_indent_str(indent) +
                  f"- Tests in test files "
                  f"with language {test_results_for_test_files.language}: "
                  f"{self.get_status_string(test_results_for_test_files.tests_are_ok)}",
                  file=self.file)

    def print_status_for_test_folders(self,
                                      test_result_of_flavor: RunDBTestsInTestConfigResult,
                                      indent: int):
        for test_results_for_test_folder in test_result_of_flavor.test_folders_output.test_results:
            print(self.get_indent_str(indent) +
                  f"- Tests in test folder {test_results_for_test_folder.test_folder} "
                  f"with language {test_results_for_test_folder.test_folder}: "
                  f"{self.get_status_string(test_results_for_test_folder.tests_are_ok)}",
                  file=self.file)

    def print_status_for_generic_language_tests(self,
                                                test_result_of_flavor: RunDBTestsInTestConfigResult,
                                                indent: int):
        for test_results_for_test_folder in test_result_of_flavor.generic_language_tests_output.test_results:
            print(self.get_indent_str(indent) +
                  f"- Tests in test folder {test_results_for_test_folder.test_folder}"
                  f"with language {test_results_for_test_folder.language}: "
                  f"{self.get_status_string(test_results_for_test_folder.tests_are_ok)}",
                  file=self.file)

    @staticmethod
    def get_indent_str(indent: int):
        return " " * indent

    @staticmethod
    def get_status_string(status: bool):
        return 'OK' if status else 'FAILED'


class TestContainer(FlavorsBaseTask,
                    TestContainerParameter,
                    SpawnTestEnvironmentParameter):
    def __init__(self, *args, **kwargs):
        self.test_results_futures = None
        super().__init__(*args, **kwargs)
        command_line_output_path = self.get_output_path().joinpath("command_line_output")
        self.command_line_output_target = luigi.LocalTarget(str(command_line_output_path))

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(
            TestFlavorContainer)  # type: Dict[str,TestFlavorContainer]
        self.test_results_futures = self.register_dependencies(tasks)

    def run_task(self):
        test_results = self.get_values_from_futures(
            self.test_results_futures)  # type: Dict[str,FlavorTestResult]
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(test_results, 4)

        with self.command_line_output_target.open("w") as file:
            TestStatusPrinter(file).print_status_for_all_tests(test_results)

        test_result = AllTestsResult(test_results_per_flavor=test_results,
                                     command_line_output_path=Path(self.command_line_output_target.path))
        self.return_object(test_result)


class TestFlavorContainer(FlavorBaseTask,
                          TestContainerParameter,
                          SpawnTestEnvironmentParameter):

    def __init__(self, *args, **kwargs):
        self.test_result_futures = None
        super().__init__(*args, **kwargs)

    def register_required(self):
        tasks = {release_goal: self.generate_tasks_for_flavor(release_goal)
                 for release_goal in self.release_goals}
        self.test_result_futures = self.register_dependencies(tasks)

    def generate_tasks_for_flavor(self, release_goal: str):
        task = self.create_child_task_with_common_params(TestRunnerDBTestTask,
                                                         release_goal=release_goal)
        return task

    def run_task(self):
        test_results = self.get_values_from_futures(
            self.test_result_futures)  # type: Dict[str,RunDBTestsInTestConfigResult]
        result = FlavorTestResult(self.flavor_path, test_results)
        JsonPickleTarget(self.get_output_path().joinpath("test_results.json")).write(test_results, 4)
        self.return_object(result)
