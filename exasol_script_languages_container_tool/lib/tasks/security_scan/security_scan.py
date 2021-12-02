from pathlib import Path
from typing import Dict

import luigi
from docker.types import Mount

from exasol_integration_test_docker_environment.lib.base.flavor_task import FlavorsBaseTask
from exasol_integration_test_docker_environment.lib.config.build_config import build_config
from exasol_integration_test_docker_environment.lib.docker import ContextDockerClient

from exasol_script_languages_container_tool.lib.tasks.build.docker_flavor_build_base import DockerFlavorBuildBase

from exasol_script_languages_container_tool.lib.tasks.security_scan.security_scan_parameter import SecurityScanParameter


class ScanResult:
    def __init__(self, is_ok, summary, report_dir):
        self.is_ok = is_ok
        self.summary = summary
        self.report_dir = report_dir


class SecurityScan(FlavorsBaseTask, SecurityScanParameter):

    def __init__(self, *args, **kwargs):
        self.security_scanner_futures = None
        super().__init__(*args, **kwargs)
        report_path = self.report_path.joinpath("security_report")
        self.security_report_target = luigi.LocalTarget(str(report_path))

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(
            SecurityScanner, report_path=self.report_path)  # type: Dict[str,SecurityScanner]
        self.security_scanner_futures = self.register_dependencies(tasks)

    def run_task(self):
        security_scanner_results = self.get_values_from_futures(
            self.security_scanner_futures)

        print(f"ScanResults:{security_scanner_results}")
        self.write_report(security_scanner_results)
        all_result = AllScanResult(security_scanner_results)
        if not all_result.scans_are_ok:
            raise RuntimeError(f"Not all security scans were successful.:\n{all_result.get_error_scans_msg()}")

    def write_report(self, security_scanner: Dict[str, ScanResult]):
        with self.security_report_target.open("w") as out_file:

            for key, value in security_scanner.items():
                out_file.write("\n")
                out_file.write(f"============ START SECURITY SCAN REPORT - <{key}> ====================")
                out_file.write("\n")
                out_file.write(f"Successful:{value.is_ok}\n")
                out_file.write(f"Full report:{value.report_dir}\n")
                out_file.write(f"Summary:\n")
                out_file.write(value.summary)
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
        flavor_path = Path(self.flavor_path)
        report_path = self.report_path.joinpath(flavor_path.name)
        report_path.mkdir(parents=True, exist_ok=True)
        report_path_abs = str(report_path.absolute())
        result = ScanResult(is_ok=False, summary="", report_dir=report_path_abs)
        assert len(task_results.values()) == 1
        for task_result in task_results.values():
            self.logger.info(f"Running security run on image:{task_result.get_target_complete_name()}, report path: "
                             f"{report_path_abs}")

            with ContextDockerClient() as docker_client:
                mounts = [Mount(source=report_path_abs, target=report_path_abs, type="bind")]
                result_container = docker_client.containers.run(task_result.get_target_complete_name(),
                                                                command=report_path_abs, mounts=mounts,
                                                                detach=True, stderr=True)
                try:
                    logs = result_container.logs(follow=True).decode("UTF-8")
                    result_container_result = result_container.wait()

                    result = ScanResult(is_ok=(result_container_result["StatusCode"] == 0),
                                        summary=logs, report_dir=report_path_abs)
                finally:
                    result_container.remove()

        self.return_object(result)


class AllScanResult:
    def __init__(self, scan_results_per_flavor: Dict[str, ScanResult]):
        self.scan_results_per_flavor = scan_results_per_flavor
        self.scans_are_ok = all(scan_result.is_ok
                                for scan_result
                                in scan_results_per_flavor.values())

    def get_error_scans_msg(self):
        return [f"{key}: '{value.summary}'" for key, value in self.scan_results_per_flavor.items() if not value.is_ok]
