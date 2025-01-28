import shutil
from pathlib import Path
from typing import Generator, Optional

import luigi
from exasol_integration_test_docker_environment.lib.base.abstract_task_future import (
    AbstractTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.info import Info

from exasol.slc.internal.tasks.export.cache_file_parameters import CacheFileParameters
from exasol.slc.internal.tasks.export.export_container_parameters import (
    CHECKSUM_ALGORITHM,
    ExportContainerParameter,
)
from exasol.slc.internal.tasks.export.export_container_to_cache_task import (
    ExportContainerToCacheTask,
)


class ExportContainerToFileInfo(Info):
    def __init__(self, is_new: bool, output_file_path: str) -> None:
        self.output_file_path = output_file_path
        self.is_new = is_new


class ExportContainerToFileTask(
    FlavorBaseTask, ExportContainerParameter, CacheFileParameters
):
    release_image_name: str = luigi.Parameter()  # type: ignore

    def run_task(self) -> Generator[BaseTask, None, None]:
        cache_file = Path(self.cache_file_path)
        checksum_file = Path(self.checksum_file_path)

        export_container_to_cache_task: ExportContainerToCacheTask = (
            self.create_child_task_with_common_params(
                ExportContainerToCacheTask,
            )
        )
        is_new_future: AbstractTaskFuture = (
            yield from self.run_dependencies(export_container_to_cache_task)
        )

        is_new: bool = self.get_values_from_futures(is_new_future)
        assert isinstance(is_new, bool)

        output_file = self._copy_cache_file_to_output_path(
            cache_file, checksum_file, is_new
        )
        export_container_to_file_info = ExportContainerToFileInfo(
            is_new, str(output_file)
        )
        self.return_object(export_container_to_file_info)

    def _copy_cache_file_to_output_path(
        self, cache_file: Path, checksum_file: Path, is_new: bool
    ) -> Optional[Path]:
        output_file = None
        if self.export_path is not None:
            if self.release_name is not None:
                suffix = f"""_{self.release_name}"""
            else:
                suffix = ""
            file_name = (
                f"""{self.get_flavor_name()}_{self.release_goal}{suffix}.tar.gz"""
            )
            output_file = Path(str(self.export_path), file_name)
            output_checksum_file = Path(
                str(self.export_path), file_name + "." + CHECKSUM_ALGORITHM
            )
            if not output_file.exists() or not output_checksum_file.exists() or is_new:
                output_file.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy2(checksum_file, output_checksum_file)
                shutil.copy2(cache_file, output_file)
        return output_file
