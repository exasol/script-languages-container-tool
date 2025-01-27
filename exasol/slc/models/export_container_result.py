from pathlib import Path
from typing import Dict

from exasol_integration_test_docker_environment.lib.base.info import Info

from exasol.slc.models.export_info import ExportInfo


class ExportContainerResult(Info):
    def __init__(
        self,
        export_infos: Dict[str, Dict[str, ExportInfo]],
        command_line_output_path: Path,
    ) -> None:
        self.export_infos = export_infos
        self.command_line_output_path = command_line_output_path
