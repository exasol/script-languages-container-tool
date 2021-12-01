import subprocess
from typing import Dict

import luigi
from docker.errors import ContainerError
from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorsBaseTask
from exasol_integration_test_docker_environment.lib.config.build_config import build_config
from exasol_integration_test_docker_environment.lib.docker import ContextDockerClient

from exasol_script_languages_container_tool.lib.tasks.build.docker_flavor_build_base import DockerFlavorBuildBase

from exasol_script_languages_container_tool.lib.tasks.security_scan.security_scan_parameter import SecurityScanParameter


class SecurityScan(FlavorsBaseTask, SecurityScanParameter):

    def __init__(self, *args, **kwargs):
        self.security_scanner_futures = None
        super().__init__(*args, **kwargs)
        report_path = self.get_output_path().joinpath("security_report")
        self.security_report_target = luigi.LocalTarget(str(report_path))

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(
            SecurityScanner)  # type: Dict[str,SecurityScanner]
        self.security_scanner_futures = self.register_dependencies(tasks)

    def run_task(self):
        security_scanner = self.get_values_from_futures(
            self.security_scanner_futures)
        self.write_report(security_scanner)

    def write_report(self, security_scanner):
        with self.security_report_target.open("w") as out_file:

            for results in security_scanner.values():
                for result_key_value in results.items():
                    key, value = result_key_value
                    out_file.write("\n")
                    out_file.write(f"============ START SECURITY SCAN REPORT - <{key}> ====================")
                    out_file.write("\n")
                    out_file.write(value)
                    out_file.write("\n")
                    out_file.write(f"============ END SECURITY SCAN REPORT - <{key}> ====================")
                    out_file.write("\n")


class SecurityScanner(DockerFlavorBuildBase, SecurityScanParameter):

    def get_goals(self):
        return {"security_scan"}

    def get_release_task(self):
        return self.create_build_tasks(not build_config().force_rebuild)

    def run_task(self):
        tasks = self.get_release_task()

        tasks_futures = yield from self.run_dependencies(tasks)
        task_results = self.get_values_from_futures(tasks_futures)
        result = ''
        assert len(task_results.values()) == 1
        for task_result in task_results.values():
            print(f"Running security run on image:{task_result.get_target_complete_name()}")
            with ContextDockerClient() as docker_client:
                result_container = docker_client.containers \
                    .run(task_result.get_target_complete_name(), detach=True, stderr=True)
                result = result_container.logs(follow=True).decode("UTF-8")
                result_container_result = result_container.wait()
                result_container.remove()
                if result_container_result["StatusCode"] != 0:
                    raise RuntimeError(f"Error running security scan:'{result}'")

        self.return_object({self.flavor_path: result})
