from collections.abc import Generator
from typing import Dict, Set

import luigi
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)
from exasol.slc.internal.tasks.export.export_container_task import ExportContainerTask
from exasol.slc.internal.tasks.export.export_container_tasks_creator import (
    ExportContainerTasksCreator,
)
from exasol.slc.internal.tasks.upload.upload_container_task import UploadContainerTask
from exasol.slc.internal.tasks.upload.upload_container_tasks_creator import (
    UploadContainerTasksCreator,
)
from exasol.slc.internal.tasks.upload.upload_containers_parameter import (
    UploadContainersParameter,
)


class UploadContainers(FlavorsBaseTask, UploadContainersParameter):

    def __init__(self, *args, **kwargs) -> None:
        self.upload_info_futures = None
        super().__init__(*args, **kwargs)
        command_line_output_path = self.get_output_path().joinpath(
            "command_line_output"
        )
        self.command_line_output_target = luigi.LocalTarget(
            str(command_line_output_path)
        )

    def register_required(self) -> None:
        tasks: dict[str, UploadFlavorContainers] = (
            self.create_tasks_for_flavors_with_common_params(UploadFlavorContainers)
        )
        self.upload_info_futures = self.register_dependencies(tasks)

    def run_task(self) -> None:
        uploads: dict[str, dict[str, str]] = self.get_values_from_futures(
            self.upload_info_futures
        )
        assert isinstance(uploads, dict)
        assert all(isinstance(x, dict) for x in uploads.values())
        assert all(isinstance(y, str) for x in uploads.values() for y in x.values())
        assert all(isinstance(y, str) for x in uploads.values() for y in x.keys())
        self.write_command_line_output(uploads)
        self.return_object(self.command_line_output_target)

    def write_command_line_output(self, uploads: dict[str, dict[str, str]]) -> None:
        with self.command_line_output_target.open("w") as out_file:
            for releases in uploads.values():
                for command_line_output_str in releases.values():
                    out_file.write(command_line_output_str)
                    out_file.write("\n")
                    out_file.write("=================================================")
                    out_file.write("\n")


class UploadFlavorContainers(DockerFlavorBuildBase, UploadContainersParameter):

    def get_goals(self) -> set[str]:
        return set(self.release_goals)

    def run_task(self) -> Generator[BaseTask, None, None]:
        build_tasks = self.create_build_tasks()

        export_tasks = self.create_export_tasks(build_tasks)
        upload_tasks = self.create_upload_tasks(export_tasks)

        command_line_output_string_futures = yield from self.run_dependencies(
            upload_tasks
        )
        command_line_output_strings: dict[str, str] = self.get_values_from_futures(
            command_line_output_string_futures
        )
        assert all(isinstance(x, str) for x in command_line_output_strings.keys())
        assert all(isinstance(x, str) for x in command_line_output_strings.values())

        self.return_object(command_line_output_strings)

    def create_upload_tasks(self, export_tasks) -> dict[str, UploadContainerTask]:
        upload_tasks_creator = UploadContainerTasksCreator(self)
        upload_tasks = upload_tasks_creator.create_upload_tasks(export_tasks)
        return upload_tasks

    def create_export_tasks(self, build_tasks) -> dict[str, ExportContainerTask]:
        export_tasks_creator = ExportContainerTasksCreator(self, export_path=None)
        export_tasks = export_tasks_creator.create_export_tasks(build_tasks)
        return export_tasks
