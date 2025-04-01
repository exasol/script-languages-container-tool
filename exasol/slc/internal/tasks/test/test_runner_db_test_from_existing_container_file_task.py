import luigi

from exasol.slc.internal.tasks.test.test_container_file_info import (
    TestContainerFileInfo,
)
from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    TestRunnerDBTestBaseTask,
)


class TestRunnerDBTestFromExistingContainerFileTask(TestRunnerDBTestBaseTask):
    use_existing_container: str = luigi.OptionalParameter()  # type: ignore

    def register_required(self) -> None:
        self.register_spawn_test_environment()

    def _get_test_container_file_info(self) -> TestContainerFileInfo:
        return TestContainerFileInfo(
            container_file=self.use_existing_container,
            target_name=self.get_flavor_name(),
            is_new=False,
        )
