from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from nox import Session


@dataclass(frozen=True)
class Config:
    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    version_file: Path = (
        Path(__file__).parent / "exasol_script_languages_container_tool" / "version.py"
    )
    path_filters: Iterable[str] = (
        "dist",
        ".eggs",
        "venv",
    )


PROJECT_CONFIG = Config()
