import os
import shlex
import shutil
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Optional

import luigi
from exasol_integration_test_docker_environment.lib.base.abstract_task_future import (
    AbstractTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import (
    DependencyLoggerBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.still_running_logger import (
    StillRunningLogger,
)
from exasol_integration_test_docker_environment.lib.logging.command_log_handler import (
    CommandLogHandler,
)
from exasol_integration_test_docker_environment.lib.models.config.build_config import (
    build_config,
)

from exasol.slc.internal.tasks.clean.clean_images import CleanExaslcFlavorImages
from exasol.slc.internal.tasks.export.cache_file_parameters import CacheFileParameters
from exasol.slc.internal.tasks.export.create_and_export_container_task import (
    CreateAndExportContainerTask,
)
from exasol.slc.internal.tasks.export.export_container_parameters import (
    CHECKSUM_ALGORITHM,
    ExportContainerParameter,
)
from exasol.slc.models.compression_strategy import CompressionStrategy


class CheckCacheFileTask(DependencyLoggerBaseTask):
    cache_file_path: str = luigi.Parameter()  # type: ignore

    def run_task(self) -> None:
        cache_file = Path(self.cache_file_path)
        self.return_object(cache_file.exists())


class TmpDirectoryMakerTask(DependencyLoggerBaseTask):
    def run_task(self) -> None:
        temp_directory = tempfile.mkdtemp(
            prefix="release_archive_", dir=build_config().temporary_base_directory
        )
        self.return_object(temp_directory)


class ExportContainerToCacheTask(
    FlavorBaseTask, ExportContainerParameter, CacheFileParameters
):
    release_image_name: str = luigi.Parameter()  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        self._check_cache_file_future: Optional[AbstractTaskFuture] = None
        self._tmp_directory: Optional[str] = None
        super().__init__(*args, **kwargs)

    def register_required(self):
        self._check_cache_file_future = self.register_dependency(
            self.create_child_task(
                task_class=CheckCacheFileTask, cache_file_path=self.cache_file_path
            )
        )

    def run_task(self) -> Generator[BaseTask, None, None]:
        assert self._check_cache_file_future is not None
        is_new: bool = self.get_values_from_future(self._check_cache_file_future)  # type: ignore
        assert isinstance(is_new, bool)

        cache_file = Path(self.cache_file_path)
        checksum_file = Path(self.checksum_file_path)

        if not is_new:
            yield from self._export_release(
                self.release_image_name, cache_file, checksum_file
            )
            is_new = True
        else:
            yield from self._cleanup_docker_image_if_needed()
        self.return_object(is_new)

    def _cleanup_tmp_directory(self):
        if self._tmp_directory is not None:
            shutil.rmtree(self._tmp_directory)

    def on_failure(self, exception):
        super().on_failure(exception)
        self._cleanup_tmp_directory()

    def on_success(self):
        super().on_success()
        self._cleanup_tmp_directory()

    def _export_release(
        self, release_image_name: str, release_file: Path, checksum_file: Path
    ) -> Generator[BaseTask, None, None]:

        self.logger.info("Create container file %s", release_file)
        self._tmp_directory = yield from self._make_temp_directory()

        tmp_container_file = yield from self._create_and_export_container(
            release_image_name
        )

        yield from self._cleanup_docker_image_if_needed()

        log_path = self.get_log_path()
        extract_dir = self._extract_exported_container(
            log_path, tmp_container_file, self._tmp_directory
        )
        Path(tmp_container_file).unlink(missing_ok=False)
        self._modify_extracted_container(extract_dir)
        self._pack_release_file(log_path, extract_dir, release_file)
        self._compute_checksum(release_file, checksum_file)

    def _cleanup_docker_image_if_needed(self) -> Generator[BaseTask, None, None]:
        if self.cleanup_docker_images:
            clean_images_task: CleanExaslcFlavorImages = (
                self.create_child_task_with_common_params(CleanExaslcFlavorImages)
            )
            yield from self.run_dependencies(clean_images_task)

    def _create_and_export_container(
        self, release_image_name
    ) -> Generator[BaseTask, None, str]:
        create_and_export_container_task: CreateAndExportContainerTask = (
            self.create_child_task(
                CreateAndExportContainerTask,
                release_image_name=release_image_name,
                temp_directory=self._tmp_directory,
            )
        )
        tmp_container_file_future = yield from self.run_dependencies(
            create_and_export_container_task
        )
        tmp_container_file: str = self.get_values_from_future(tmp_container_file_future)  # type: ignore
        assert isinstance(tmp_container_file, str)
        return tmp_container_file

    def _make_temp_directory(self) -> Generator[BaseTask, None, str]:
        make_temp_dir_task: TmpDirectoryMakerTask = self.create_child_task(
            TmpDirectoryMakerTask,
        )
        tmp_dir_futures = yield from self.run_dependencies(make_temp_dir_task)
        tmp_directory = self.get_values_from_future(tmp_dir_futures)
        assert isinstance(tmp_directory, str)
        return tmp_directory

    def _compute_checksum(self, release_file: Path, checksum_file: Path) -> None:
        self.logger.info("Compute checksum for container file %s", release_file)
        command = f"""{CHECKSUM_ALGORITHM} '{release_file}'"""
        completed_process = subprocess.run(shlex.split(command), capture_output=True)
        completed_process.check_returncode()
        stdout = completed_process.stdout.decode("utf-8")
        stdout = stdout.replace(str(release_file), release_file.name)
        with open(checksum_file, "w") as f:
            f.write(stdout)

    def _pack_release_file(
        self, log_path: Path, extract_dir: str, release_file: Path
    ) -> None:
        self.logger.info("Pack container file %s", release_file)
        extract_content = " ".join(f"'{file}'" for file in os.listdir(extract_dir))
        if str(release_file).endswith("tar.gz"):
            tmp_release_file = release_file.with_suffix(
                ""
            )  # cut off ".gz" from ".tar.gz"
        elif str(release_file).endswith("tar"):
            tmp_release_file = release_file
        else:
            raise ValueError(
                f"Unexpected release file: '{release_file}'. Expected suffix: 'tar.gz' or 'tar'."
            )

        command = (
            f"""tar -C '{extract_dir}' -vcf '{tmp_release_file}' {extract_content}"""
        )
        self.run_command(
            command,
            f"packing container file {tmp_release_file}",
            log_path.joinpath("pack_release_file.log"),
        )
        manifest_file = os.path.join(extract_dir, "exasol-manifest.json")
        with open(manifest_file, "w") as f:
            print("{}", file=f)
        command = (
            f"""tar -C '{extract_dir}' -rvf '{tmp_release_file}' exasol-manifest.json"""
        )
        self.run_command(
            command,
            f"adding manifest to '{tmp_release_file}'",
            log_path.joinpath("pack_release_file.log"),
        )
        shutil.rmtree(extract_dir)
        if self.compression_strategy == CompressionStrategy.GZIP:
            command = f"""gzip {tmp_release_file}"""
            self.run_command(
                command,
                f"Creating '{release_file}'",
                log_path.joinpath("pack_release_file.log"),
            )
        elif self.compression_strategy == CompressionStrategy.NONE:
            pass
        else:
            raise ValueError(
                f"Unexpected compression_strategy: {self.compression_strategy}"
            )

    @staticmethod
    def _modify_extracted_container(extract_dir: str) -> None:
        os.symlink("/conf/resolv.conf", f"""{extract_dir}/etc/resolv.conf""")
        os.symlink("/conf/hosts", f"""{extract_dir}/etc/hosts""")

    def _extract_exported_container(
        self, log_path: Path, export_file: str, temp_directory: str
    ) -> str:
        self.logger.info("Extract exported file %s", export_file)
        extract_dir = temp_directory + "/extract"
        os.makedirs(extract_dir)
        excludes = " ".join(
            [
                "--exclude='%s'" % directory
                for directory in [
                    "dev/*",
                    "proc/*",
                    "etc/resolv.conf",
                    "etc/hosts",
                    "var/cache/apt",
                    "var/lib/apt",
                    "var/lib/dpkg",
                ]
            ]
        )
        self.run_command(
            f"""tar {excludes} -xvf '{export_file}' -C '{extract_dir}'""",
            "extracting exported container %s" % export_file,
            log_path.joinpath("extract_release_file.log"),
        )
        return extract_dir

    def run_command(self, command: str, description: str, log_file_path: Path) -> None:
        with subprocess.Popen(
            shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as process:
            with CommandLogHandler(
                log_file_path, self.logger, description
            ) as log_handler:
                still_running_logger = StillRunningLogger(self.logger, description)
                log_handler.handle_log_lines((command + "\n").encode("utf-8"))

                if stdout := process.stdout:
                    for line in iter(stdout.readline, b""):
                        still_running_logger.log()
                        log_handler.handle_log_lines(line)
                process.wait(timeout=60 * 2)
                return_code_log_line = "return code %s" % process.returncode
                log_handler.handle_log_lines(
                    return_code_log_line.encode("utf-8"), process.returncode != 0
                )
