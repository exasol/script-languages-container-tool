from pathlib import Path
from typing import Dict

from exasol_integration_test_docker_environment.lib.base.info import Info


class ScanResult(Info):
    def __init__(self, is_ok: bool, summary: str, report_dir: Path) -> None:
        self.is_ok = is_ok
        self.summary = summary
        self.report_dir = report_dir


class AllScanResult(Info):
    def __init__(
        self, scan_results_per_flavor: dict[str, ScanResult], report_path: Path
    ) -> None:
        self.scan_results_per_flavor = scan_results_per_flavor
        self.scans_are_ok = all(
            scan_result.is_ok for scan_result in scan_results_per_flavor.values()
        )
        self.report_path = report_path

    def get_error_scans_msg(self):
        return [
            f"{key}: '{value.summary}'"
            for key, value in self.scan_results_per_flavor.items()
            if not value.is_ok
        ]
