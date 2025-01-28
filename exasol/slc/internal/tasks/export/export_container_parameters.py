from typing import Optional, Tuple

import luigi
from luigi import Config

CHECKSUM_ALGORITHM = "sha512sum"


class ExportContainerParameterBase(Config):
    export_path: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    release_name: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    cleanup_docker_images: bool = luigi.BoolParameter(False)  # type: ignore


class ExportContainerParameter(ExportContainerParameterBase):
    release_goal: str = luigi.Parameter()  # type: ignore


class ExportContainersParameter(ExportContainerParameterBase):
    release_goals: Tuple[str, ...] = luigi.ListParameter(["release"])  # type: ignore
