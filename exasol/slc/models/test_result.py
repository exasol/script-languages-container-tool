from pathlib import Path
from typing import Dict

from exasol_integration_test_docker_environment.lib.base.info import Info

from exasol.slc.models.run_db_test_result import RunDBTestsInTestConfigResult


class FlavorTestResult:
    def __init__(
        self,
        flavor_path: str,
        test_results_per_release_goal: dict[str, RunDBTestsInTestConfigResult],
    ) -> None:
        self.flavor_path = str(flavor_path)
        self.test_results_per_release_goal = test_results_per_release_goal
        self.tests_are_ok = all(
            test_result.tests_are_ok
            for test_result in test_results_per_release_goal.values()
        )


class AllTestsResult(Info):
    def __init__(
        self,
        test_results_per_flavor: dict[str, FlavorTestResult],
        command_line_output_path: Path,
    ) -> None:
        self.test_results_per_flavor = test_results_per_flavor
        self.tests_are_ok = all(
            test_result.tests_are_ok for test_result in test_results_per_flavor.values()
        )
        self.command_line_output_path = command_line_output_path
