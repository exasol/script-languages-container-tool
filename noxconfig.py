from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from exasol.toolbox.util.version import Version
from pydantic import computed_field


class Config(BaseConfig):
    @computed_field  # type: ignore[misc]
    @property
    def extended_python_versions(self) -> list[str]:
        """
        Lowest and highest versions from ``python_versions``.

        Used by the slow-checks workflow to run expensive integration/GPU
        tests against only the two extreme Python versions instead of the
        full matrix.
        """
        versions = sorted(self.python_versions, key=Version.from_string)
        return sorted({versions[0], versions[-1]}, key=Version.from_string)


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="slc",
    python_versions=("3.10", "3.11", "3.12", "3.13", "3.14"),
    exasol_versions=(),
    add_to_excluded_python_paths=("test/resources", ".dependencies"),
)
