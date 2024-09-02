import tarfile
from pathlib import Path
from typing import Dict

import luigi
from docker.models.containers import Container
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorsBaseTask,
)
from exasol_integration_test_docker_environment.lib.config.build_config import (
    build_config,
)

from exasol.slc.internal.tasks.build.docker_flavor_build_base import (
    DockerFlavorBuildBase,
)
from exasol.slc.internal.tasks.security_scan.security_scan_parameter import (
    SecurityScanParameter,
)
from exasol.slc.internal.utils.tar_safe_extract import safe_extract
from exasol.slc.models.security_scan_result import AllScanResult, ScanResult


class SecurityScan(FlavorsBaseTask, SecurityScanParameter):

    def __init__(self, *args, **kwargs):
        self.security_scanner_futures = None
        super().__init__(*args, **kwargs)
        report_path = Path(self.report_path).joinpath("security_report")
        self.security_report_target = luigi.LocalTarget(str(report_path))

    def register_required(self):
        tasks = self.create_tasks_for_flavors_with_common_params(  # type: ignore
            SecurityScanner, report_path=self.report_path
        )  # type: Dict[str,SecurityScanner]
        self.security_scanner_futures = self.register_dependencies(tasks)

    def run_task(self):
        security_scanner_results = self.get_values_from_futures(
            self.security_scanner_futures
        )

        self.write_report(security_scanner_results)
        all_result = AllScanResult(
            security_scanner_results, Path(self.security_report_target.path)
        )
        self.return_object(all_result)

    def write_report(self, security_scanner: Dict[str, ScanResult]):
        with self.security_report_target.open("w") as out_file:

            for key, value in security_scanner.items():
                out_file.write("\n")
                out_file.write(
                    f"============ START SECURITY SCAN REPORT - <{key}> ===================="
                )
                out_file.write("\n")
                out_file.write(f"Successful:{value.is_ok}\n")
                out_file.write(f"Full report:{value.report_dir}\n")
                out_file.write(f"Summary:\n")
                out_file.write(value.summary)
                out_file.write("\n")
                out_file.write(
                    f"============ END SECURITY SCAN REPORT - <{key}> ===================="
                )
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
        report_path = Path(self.report_path).joinpath(flavor_path.name)
        report_path.mkdir(parents=True, exist_ok=True)
        report_path_abs = report_path.absolute()
        result = ScanResult(is_ok=False, summary="", report_dir=report_path_abs)
        assert len(task_results.values()) == 1
        for task_result in task_results.values():
            self.logger.info(
                f"Running security run on image: {task_result.get_target_complete_name()}, report path: "
                f"{report_path_abs}"
            )

            report_local_path = "/report"
            with self._get_docker_client() as docker_client:
                result_container = docker_client.containers.run(
                    task_result.get_target_complete_name(),
                    command=report_local_path,
                    detach=True,
                    stderr=True,
                )
                try:
                    logs = result_container.logs(follow=True).decode("UTF-8")
                    result_container_result = result_container.wait()
                    # We don't use mount binding here to exchange the report files, but download them from the container
                    # Thus we avoid that the files are created by root
                    self._write_report(
                        result_container, report_path_abs, report_local_path
                    )
                    result = ScanResult(
                        is_ok=(result_container_result["StatusCode"] == 0),
                        summary=logs,
                        report_dir=report_path_abs,
                    )
                finally:
                    result_container.remove()

        self.return_object(result)

    def _write_report(
        self, container: Container, report_path_abs: Path, report_local_path: str
    ):
        tar_file_path = report_path_abs / "report.tar"
        with open(tar_file_path, "wb") as tar_file:
            bits, stat = container.get_archive(report_local_path)
            for chunk in bits:
                tar_file.write(chunk)
        with tarfile.open(tar_file_path) as tar_file:
            safe_extract(tar_file, path=report_path_abs)  # type: ignore
