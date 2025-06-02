from typing import Tuple

import luigi
from luigi import Config


class DockerSaveParameter(Config):
    force_save: bool = luigi.BoolParameter(False)  # type: ignore
    save_all: bool = luigi.BoolParameter(False)  # type: ignore
    save_path: str = luigi.Parameter()  # type: ignore
    goals: tuple[str, ...] = luigi.ListParameter([])  # type: ignore
