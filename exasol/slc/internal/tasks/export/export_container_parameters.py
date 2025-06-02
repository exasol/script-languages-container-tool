from typing import Optional, Tuple

import luigi

from exasol.slc.models.compression_strategy import (
    CompressionStrategy,
    defaultCompressionStrategy,
)

CHECKSUM_ALGORITHM = "sha512sum"


class ExportContainerOptionsParameter:
    compression_strategy: CompressionStrategy = luigi.EnumParameter(enum=CompressionStrategy, default=defaultCompressionStrategy())  # type: ignore


class ExportContainerParameterBase(ExportContainerOptionsParameter):
    export_path: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    release_name: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    cleanup_docker_images: bool = luigi.BoolParameter(False)  # type: ignore


class ExportContainerParameter(ExportContainerParameterBase):
    release_goal: str = luigi.Parameter()  # type: ignore


class ExportContainersParameter(ExportContainerParameterBase):
    release_goals: tuple[str, ...] = luigi.ListParameter(["release"])  # type: ignore
