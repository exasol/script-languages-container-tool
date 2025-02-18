import os
from pathlib import Path

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.models.config.build_config import (
    build_config,
)

from exasol.slc.internal.tasks.export.cache_file_parameters import CacheFileParameters


class RemoveCachedExportTask(BaseTask, CacheFileParameters):

    def run_task(self) -> None:
        self._remove_cached_exported_file_if_requested(
            Path(self.cache_file_path), Path(self.checksum_file_path)
        )

    def _remove_cached_exported_file_if_requested(
        self, release_file: Path, checksum_file: Path
    ) -> None:
        if release_file.exists() and (
            build_config().force_rebuild
            or build_config().force_pull
            or not checksum_file.exists()
        ):
            self.logger.info("Removed container file %s", release_file)
            os.remove(release_file)
            if checksum_file.exists():
                os.remove(checksum_file)
