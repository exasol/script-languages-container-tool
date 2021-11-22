from typing import Dict

import luigi
from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorsBaseTask

from exasol_script_languages_container_tool.lib.tasks.build.docker_flavor_build_base import DockerFlavorBuildBase
from exasol_script_languages_container_tool.lib.tasks.export.export_container_tasks_creator import \
    ExportContainerTasksCreator
from exasol_script_languages_container_tool.lib.tasks.security_scan.security_scan_parameter import SecurityScanParameter
from exasol_script_languages_container_tool.lib.tasks.security_scan.security_scan_tasks_creator import \
    SecurityScannerTasksCreator


class SecurityScan(FlavorsBaseTask, SecurityScanParameter):

    def __init__(self, *args, **kwargs):
        self.security_scanner_futures = None
        super().__init__(*args, **kwargs)
        command_line_output_path = self.get_output_path().joinpath("command_line_output")
        self.command_line_output_target = luigi.LocalTarget(str(command_line_output_path))

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(
            SecurityScanner)  # type: Dict[str,SecurityScanner]
        self.security_scanner_futures = self.register_dependencies(tasks)

    def run_task(self):
        security_scanner = self.get_values_from_futures(
            self.security_scanner_futures)
        self.write_command_line_output(security_scanner)

    def write_command_line_output(self, security_scanner):
        with self.command_line_output_target.open("w") as out_file:
            for releases in security_scanner.values():
                for command_line_output_str in releases.values():
                    out_file.write(command_line_output_str)
                    out_file.write("\n")
                    out_file.write("=================================================")
                    out_file.write("\n")


class SecurityScanner(DockerFlavorBuildBase, SecurityScanParameter):

    def get_goals(self):
        return set(self.release_goals)

    def run_task(self):
        build_tasks = self.create_build_tasks()

        export_tasks = self.create_export_tasks(build_tasks)
        security_scanner_tasks = self.create_security_scanner_tasks(export_tasks)

        command_line_output_string_futures = yield from self.run_dependencies(security_scanner_tasks)
        command_line_output_strings = self.get_values_from_futures(command_line_output_string_futures)
        self.return_object(command_line_output_strings)

    def create_security_scanner_tasks(self, export_tasks):
        security_scanner_tasks_creator = SecurityScannerTasksCreator(self)
        upload_tasks = security_scanner_tasks_creator.create_upload_tasks(export_tasks)
        return upload_tasks

    def create_export_tasks(self, build_tasks):
        export_tasks_creator = ExportContainerTasksCreator(self, export_path=None)
        export_tasks = export_tasks_creator.create_export_tasks(build_tasks)
        return export_tasks
