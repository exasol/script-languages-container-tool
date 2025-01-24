import logging
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import humanfriendly
import luigi
from exasol_integration_test_docker_environment.lib.base.abstract_task_future import (
    AbstractTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.still_running_logger import (
    StillRunningLogger,
)
from exasol_integration_test_docker_environment.lib.config.build_config import (
    build_config,
)
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
)
from exasol_integration_test_docker_environment.lib.logging.command_log_handler import (
    CommandLogHandler,
)

from exasol.slc.internal.tasks.export.create_export_directory import (
    CreateExportDirectory,
)
from exasol.slc.models.export_info import ExportInfo

CHECKSUM_ALGORITHM = "sha512sum"


class ExportContainerBaseTask(FlavorBaseTask):
    task_logger = logging.getLogger("luigi-interface")
    export_path: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    release_name: Optional[str] = luigi.OptionalParameter(None)  # type: ignore
    release_goal: str = luigi.Parameter(None)  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        self._export_directory_future: Optional[AbstractTaskFuture] = None
        self._release_task_future: Optional[AbstractTaskFuture] = None
        super().__init__(*args, **kwargs)

        if self.export_path is not None:
            assert isinstance(self.export_path, str)
        if self.release_name is not None:
            assert isinstance(self.release_name, str)
        assert isinstance(self.release_goal, str)

    def register_required(self) -> None:
        self._export_directory_future = self.register_dependency(
            self.create_child_task(task_class=CreateExportDirectory)
        )
        if release_task := self.get_release_task():
            self._release_task_future = self.register_dependency(release_task)

    def get_release_task(self) -> Optional[BaseTask]:
        pass

    def run_task(self) -> None:
        assert self._export_directory_future is not None
        assert self._release_task_future is not None
        image_info_of_release_image: ImageInfo = self._release_task_future.get_output()
        assert isinstance(image_info_of_release_image, ImageInfo)
        cache_file, release_complete_name, release_image_name = (
            self._get_cache_file_path(
                image_info_of_release_image, self._export_directory_future
            )
        )
        checksum_file = Path(str(cache_file) + "." + CHECKSUM_ALGORITHM)
        self._remove_cached_exported_file_if_requested(cache_file, checksum_file)

        is_new = False
        if not cache_file.exists():
            self._export_release(release_image_name, cache_file, checksum_file)
            is_new = True
        output_file = self._copy_cache_file_to_output_path(
            cache_file, checksum_file, is_new
        )
        export_info = self._create_export_info(
            image_info_of_release_image,
            release_complete_name,
            cache_file,
            is_new,
            output_file,
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

    def _get_cache_file_path(
        self,
        image_info_of_release_image: ImageInfo,
        export_directory_future: AbstractTaskFuture,
    ) -> Tuple[Path, str, str]:
        release_image_name = image_info_of_release_image.get_target_complete_name()
        export_path = Path(export_directory_future.get_output()).absolute()
        release_complete_name = f"""{image_info_of_release_image.target_tag}-{image_info_of_release_image.hash}"""
        cache_file = Path(export_path, release_complete_name + ".tar.gz").absolute()
        return cache_file, release_complete_name, release_image_name

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

    def _remove_cached_exported_file_if_requested(
        self, release_file: Path, checksum_file: Path
    ) -> None:
        if release_file.exists() and (
            build_config().force_rebuild
            or build_config().force_pull
            or not checksum_file.exists()
        ):
            self.task_logger.info("Removed container file %s", release_file)
            os.remove(release_file)
            if checksum_file.exists():
                os.remove(checksum_file)

    def _export_release(
        self, release_image_name: str, release_file: Path, checksum_file: Path
    ) -> None:
        self.task_logger.info("Create container file %s", release_file)
        temp_directory = tempfile.mkdtemp(
            prefix="release_archive_", dir=build_config().temporary_base_directory
        )
        try:
            log_path = self.get_log_path()
            export_file = self._create_and_export_container(
                release_image_name, temp_directory
            )
            extract_dir = self._extract_exported_container(
                log_path, export_file, temp_directory
            )
            self._modify_extracted_container(extract_dir)
            self._pack_release_file(log_path, extract_dir, release_file)
            self._compute_checksum(release_file, checksum_file)
        finally:
            shutil.rmtree(temp_directory)

    def _compute_checksum(self, release_file: Path, checksum_file: Path) -> None:
        self.task_logger.info("Compute checksum for container file %s", release_file)
        command = f"""{CHECKSUM_ALGORITHM} '{release_file}'"""
        completed_process = subprocess.run(shlex.split(command), capture_output=True)
        completed_process.check_returncode()
        stdout = completed_process.stdout.decode("utf-8")
        stdout = stdout.replace(str(release_file), release_file.name)
        with open(checksum_file, "w") as f:
            f.write(stdout)

    def _create_and_export_container(
        self, release_image_name: str, temp_directory: str
    ) -> str:
        self.task_logger.info("Export container %s", release_image_name)
        with self._get_docker_client() as docker_client:
            container = docker_client.containers.create(image=release_image_name)
            try:
                return self._export_container(
                    container, release_image_name, temp_directory
                )
            finally:
                container.remove(force=True)

    def _export_container(
        self, container, release_image_name: str, temp_directory: str
    ) -> str:
        generator = container.export(chunk_size=humanfriendly.parse_size("10mb"))
        export_file = temp_directory + "/export.tar"
        with open(export_file, "wb") as file:
            still_running_logger = StillRunningLogger(
                self.logger, "Export image %s" % release_image_name
            )
            for chunk in generator:
                still_running_logger.log()
                file.write(chunk)
        return export_file

    def _pack_release_file(
        self, log_path: Path, extract_dir: str, release_file: Path
    ) -> None:
        self.task_logger.info("Pack container file %s", release_file)
        extract_content = " ".join(f"'{file}'" for file in os.listdir(extract_dir))
        if not str(release_file).endswith("tar.gz"):
            raise ValueError(
                f"Unexpected release file: '{release_file}'. Expected suffix 'tar.gz'."
            )
        tmp_release_file = release_file.with_suffix("")  # cut off ".gz" from ".tar.gz"
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
        command = f"""gzip {tmp_release_file}"""
        self.run_command(
            command,
            f"Creating '{release_file}'",
            log_path.joinpath("pack_release_file.log"),
        )

    @staticmethod
    def _modify_extracted_container(extract_dir: str) -> None:
        os.symlink("/conf/resolv.conf", f"""{extract_dir}/etc/resolv.conf""")
        os.symlink("/conf/hosts", f"""{extract_dir}/etc/hosts""")

    def _extract_exported_container(
        self, log_path: Path, export_file: str, temp_directory: str
    ) -> str:
        self.task_logger.info("Extract exported file %s", export_file)
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
