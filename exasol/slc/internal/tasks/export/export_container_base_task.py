from collections.abc import Generator
from pathlib import Path
from typing import Optional, Tuple

from exasol_integration_test_docker_environment.lib.base.abstract_task_future import (
    AbstractTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
)

from exasol.slc.internal.tasks.export.create_export_directory import (
    CreateExportDirectory,
)
from exasol.slc.internal.tasks.export.export_container_parameters import (
    CHECKSUM_ALGORITHM,
    ExportContainerParameter,
)
from exasol.slc.internal.tasks.export.export_container_to_file_task import (
    ExportContainerToFileInfo,
    ExportContainerToFileTask,
)
from exasol.slc.internal.tasks.export.remove_cached_export_file_task import (
    RemoveCachedExportTask,
)
from exasol.slc.models.compression_strategy import CompressionStrategy
from exasol.slc.models.export_info import ExportInfo


class ExportContainerBaseTask(FlavorBaseTask, ExportContainerParameter):

    def __init__(self, *args, **kwargs) -> None:
        self._export_directory_future: Optional[AbstractTaskFuture] = None
        self._release_task_future: Optional[AbstractTaskFuture] = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        self._export_directory_future = self.register_dependency(
            self.create_child_task(task_class=CreateExportDirectory)
        )
        if release_task := self.get_release_task():
            self._release_task_future = self.register_dependency(release_task)

    def get_release_task(self) -> Optional[BaseTask]:
        pass

    def run_task(self) -> Generator[BaseTask, None, None]:
        assert self._export_directory_future is not None
        assert self._release_task_future is not None
        image_info_of_release_image: ImageInfo = self._release_task_future.get_output()
        assert isinstance(image_info_of_release_image, ImageInfo)
        cache_file, release_complete_name, release_image_name = (
            self._get_cache_file_path(
                image_info_of_release_image, self._export_directory_future
            )
        )
        checksum_file = f"{cache_file}.{CHECKSUM_ALGORITHM}"
        remove_cached_export_file_task: RemoveCachedExportTask = self.create_child_task(
            RemoveCachedExportTask,
            cache_file_path=cache_file,
            checksum_file_path=checksum_file,
        )
        yield from self.run_dependencies(remove_cached_export_file_task)

        export_container_to_file_task: ExportContainerToFileTask = (
            self.create_child_task_with_common_params(
                ExportContainerToFileTask,
                cache_file_path=cache_file,
                checksum_file_path=checksum_file,
                release_image_name=release_image_name,
            )
        )
        export_container_to_file_result_future: AbstractTaskFuture = (
            yield from self.run_dependencies(export_container_to_file_task)
        )

        export_container_to_file_result: ExportContainerToFileInfo = (
            self.get_values_from_futures(export_container_to_file_result_future)
        )
        assert isinstance(export_container_to_file_result, ExportContainerToFileInfo)

        cache_file_path = Path(cache_file)
        export_info = self._create_export_info(
            image_info_of_release_image,
            release_complete_name,
            cache_file_path,
            export_container_to_file_result.is_new,
            Path(export_container_to_file_result.output_file_path),
        )
        self.return_object(export_info)

    def _create_export_info(
        self,
        image_info_of_release_image: ImageInfo,
        release_complete_name: str,
        cache_file: Path,
        is_new: bool,
        output_file: Optional[Path],
    ) -> ExportInfo:
        export_info = ExportInfo(
            cache_file=str(cache_file),
            complete_name=release_complete_name,
            name=self.get_flavor_name(),
            _hash=str(image_info_of_release_image.hash),
            is_new=is_new,
            depends_on_image=image_info_of_release_image,
            release_goal=str(self.release_goal),
            release_name=str(self.release_name),
            output_file=str(output_file) if output_file else None,
        )
        return export_info

    def _get_export_file_extension(self) -> str:
        if self.compression_strategy == CompressionStrategy.GZIP:
            return ".tar.gz"
        elif self.compression_strategy == CompressionStrategy.NONE:
            return ".tar"
        else:
            raise ValueError(
                f"Unsupported compression_strategy: {self.compression_strategy}"
            )

    def _get_cache_file_path(
        self,
        image_info_of_release_image: ImageInfo,
        export_directory_future: AbstractTaskFuture,
    ) -> tuple[str, str, str]:
        release_image_name = image_info_of_release_image.get_target_complete_name()
        export_path = Path(export_directory_future.get_output()).absolute()
        release_complete_name = f"""{image_info_of_release_image.target_tag}-{image_info_of_release_image.hash}"""
        cache_file = Path(
            export_path, release_complete_name + self._get_export_file_extension()
        ).absolute()
        return str(cache_file), release_complete_name, release_image_name
