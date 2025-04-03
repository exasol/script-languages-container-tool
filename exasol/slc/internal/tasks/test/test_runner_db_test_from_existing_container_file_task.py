import luigi

from exasol.slc.internal.tasks.test.container_file_under_test_info import (
    ContainerFileUnderTestInfo,
)
from exasol.slc.internal.tasks.test.test_runner_db_test_base_task import (
    TestRunnerDBTestBaseTask,
)


class TestRunnerDBTestFromExistingContainerFileTask(TestRunnerDBTestBaseTask):
    use_existing_container: str = luigi.OptionalParameter()  # type: ignore

    def register_required(self) -> None:
        self.register_spawn_test_environment()

    def _get_container_file_under_test_info(self) -> ContainerFileUnderTestInfo:
        # explicitly set is_new to "False" in order to avoid upload of SLC to BucketFS
        # if the user has explicitly set "self.reuse_uploaded_container"
        # as there is no way to check if the external file has been changed.
        # => The user is responsible for uploading/not uploading the file to BucketFS.
        return ContainerFileUnderTestInfo(
            container_file=self.use_existing_container,
            target_name=self.get_flavor_name(),
            is_new=False,
        )
