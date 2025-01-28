import humanfriendly
import luigi
from exasol_integration_test_docker_environment.lib.base.docker_base_task import (
    DockerBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.still_running_logger import (
    StillRunningLogger,
)


class CreateAndExportContainerTask(DockerBaseTask):
    release_image_name: str = luigi.Parameter()  # type: ignore
    temp_directory: str = luigi.Parameter()  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run_task(self) -> None:
        temp_export_file = self._create_and_export_container(
            self.release_image_name, self.temp_directory
        )
        self.return_object(temp_export_file)

    def _create_and_export_container(
        self, release_image_name: str, temp_directory: str
    ) -> str:
        self.logger.info("Export container %s", release_image_name)
        with self._get_docker_client() as docker_client:
            container = docker_client.containers.create(image=release_image_name)
            try:
                return self._export_container(
                    container, release_image_name, temp_directory
                )
            finally:
                container.remove(force=True)

    def _export_container(
        self, container, release_image_name: str, temp_directory: str
    ) -> str:
        generator = container.export(chunk_size=humanfriendly.parse_size("10mb"))
        export_file = temp_directory + "/export.tar"
        with open(export_file, "wb") as file:
            still_running_logger = StillRunningLogger(
                self.logger, "Export image %s" % release_image_name
            )
            for chunk in generator:
                still_running_logger.log()
                file.write(chunk)

        return export_file
