from pathlib import Path
from typing import Dict

import luigi
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.config.build_config import (
    build_config,
)
from luigi import Config

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)
from exasol.slc.internal.tasks.export.export_container_tasks_creator import (
    ExportContainerTasksCreator,
)
from exasol.slc.models.export_container_result import ExportContainerResult
from exasol.slc.models.export_info import ExportInfo


class ExportContainerParameter(Config):
    release_goals = luigi.ListParameter(["release"])
    export_path = luigi.OptionalParameter(None)
    release_name = luigi.OptionalParameter(None)
    # TOOD force export


class ExportContainers(FlavorsBaseTask, ExportContainerParameter):

    def __init__(self, *args, **kwargs):
        self.export_info_futures = None
        super().__init__(*args, **kwargs)
        command_line_output_path = self.get_output_path().joinpath(
            "command_line_output"
        )
        self.command_line_output_target = luigi.LocalTarget(
            str(command_line_output_path)
        )

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(  # type: ignore
            ExportFlavorContainer
        )  # type: Dict[str,ExportFlavorContainer]
        self.export_info_futures = self.register_dependencies(tasks)

    def run_task(self):
        export_infos = self.get_values_from_futures(  # type: ignore
            self.export_info_futures
        )  # type: Dict[str,Dict[str,ExportInfo]]
        self.write_command_line_output(export_infos)
        result = ExportContainerResult(
            export_infos, Path(self.command_line_output_target.path)
        )
        self.return_object(result)

    def write_command_line_output(self, export_infos: Dict[str, Dict[str, ExportInfo]]):
        if self.command_line_output_target.exists():
            self.command_line_output_target.remove()
        with self.command_line_output_target.open("w") as out_file:
            for flavor_path, releases in export_infos.items():
                for release_name, export_info in releases.items():
                    out_file.write("\n")
                    out_file.write("Cached container under %s" % export_info.cache_file)
                    out_file.write("\n")
                    out_file.write("\n")
                    if (
                        export_info.output_file is not None
                        and export_info.output_file != "None"
                    ):
                        out_file.write(
                            "Copied container to %s" % export_info.output_file
                        )
                        out_file.write("\n")
                        out_file.write("\n")
                    out_file.write("=================================================")
                    out_file.write("\n")


class ExportFlavorContainer(DockerFlavorBuildBase, ExportContainerParameter):

    def get_goals(self):
        return set(self.release_goals)

    def run_task(self):
        build_tasks = self.create_build_tasks(not build_config().force_rebuild)
        tasks_creator = ExportContainerTasksCreator(self, self.export_path)
        export_tasks = tasks_creator.create_export_tasks(build_tasks)
        export_info_futures = yield from self.run_dependencies(export_tasks)
        export_infos = self.get_values_from_futures(export_info_futures)
        self.return_object(export_infos)
