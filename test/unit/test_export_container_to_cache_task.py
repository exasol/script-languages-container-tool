import logging
from pathlib import Path

from exasol.slc.internal.tasks.export.export_container_to_cache_task import (
    ExportContainerToCacheTask,
)


def test_extract_exported_container_keeps_dpkg(tmp_path: Path):
    task = ExportContainerToCacheTask.__new__(ExportContainerToCacheTask)
    task.logger = logging.getLogger("test")

    captured = {}

    def fake_run_command(command: str, description: str, log_file_path: Path) -> None:
        captured["command"] = command
        captured["description"] = description
        captured["log_file_path"] = log_file_path

    task.run_command = fake_run_command  # type: ignore[method-assign]

    extract_dir = task._extract_exported_container(
        tmp_path / "log",
        str(tmp_path / "export.tar"),
        str(tmp_path),
    )

    assert extract_dir == f"{tmp_path}/extract"
    assert "var/lib/dpkg" not in captured["command"]
    assert "var/lib/apt" in captured["command"]
    assert captured["description"] == f"extracting exported container {tmp_path / 'export.tar'}"
    assert captured["log_file_path"] == tmp_path / "log" / "extract_release_file.log"
