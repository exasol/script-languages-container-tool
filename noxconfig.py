from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from nox import Session


@dataclass(frozen=True)
class Config:
    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    version_file: Path = Path(__file__).parent / "exasol" / "slc" / "version.py"
    path_filters: Iterable[str] = ("dist", ".eggs", "venv", "resources")


PROJECT_CONFIG = Config()
