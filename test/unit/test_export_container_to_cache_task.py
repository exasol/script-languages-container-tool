from pathlib import Path
from unittest.mock import Mock, patch

from exasol.slc.internal.tasks.export.export_container_to_cache_task import (
    ExportContainerToCacheTask,
)


def test_extract_exported_container_keeps_dpkg(tmp_path: Path):
    # Bypass Luigi task initialization so the test can exercise the private helper directly.
    task = ExportContainerToCacheTask.__new__(ExportContainerToCacheTask)
    task.logger = Mock()

    with patch.object(task, "run_command") as mock_run_command:
        extract_dir = task._extract_exported_container(
            tmp_path / "log",
            str(tmp_path / "export.tar"),
            str(tmp_path),
        )

    assert extract_dir == f"{tmp_path}/extract"
    mock_run_command.assert_called_once()
    command, description, log_file_path = mock_run_command.call_args.args
    assert "var/lib/dpkg" not in command
    assert "var/lib/apt" in command
    assert description == f"extracting exported container {tmp_path / 'export.tar'}"
    assert log_file_path == tmp_path / "log" / "extract_release_file.log"
