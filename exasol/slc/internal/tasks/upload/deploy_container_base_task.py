from pathlib import Path
from typing import Any, Optional

import exasol.bucketfs as bfs  # type: ignore
import luigi
from exasol_integration_test_docker_environment.abstract_method_exception import (
    AbstractMethodException,
)
from exasol_integration_test_docker_environment.lib.base.abstract_task_future import (
    AbstractTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.base_task import (
    RequiresTaskFuture,
)
from exasol_integration_test_docker_environment.lib.base.flavor_task import (
    FlavorBaseTask,
)

from exasol.slc.internal.tasks.upload.deploy_info import DeployInfo
from exasol.slc.internal.tasks.upload.language_def_parser import (
    parse_language_definition,
)
from exasol.slc.internal.tasks.upload.language_definition import LanguageDefinition
from exasol.slc.internal.tasks.upload.upload_container_parameter import (
    UploadContainerParameter,
)
from exasol.slc.internal.utils.file_utilities import detect_container_file_extension
from exasol.slc.models.export_info import ExportInfo
from exasol.slc.models.language_definition_components import (
    LanguageDefinitionComponents,
)
from exasol.slc.models.language_definitions_builder import LanguageDefinitionsBuilder


class DeployContainerBaseTask(FlavorBaseTask, UploadContainerParameter):
    # TODO check if upload was successfull by requesting the file
    # TODO add error checks and propose reasons for the error
    # TODO extract bucketfs interaction into own module

    release_goal: str = luigi.Parameter()  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        self.export_info_future: Optional[AbstractTaskFuture] = None
        super().__init__(*args, **kwargs)

    def register_required(self) -> None:
        if task := self.get_export_task():
            self.export_info_future = self.register_dependency(task)

    def get_export_task(self) -> Optional[Any]:
        raise AbstractMethodException()

    def run_task(self) -> None:
        assert self.export_info_future is not None
        export_info = self.get_values_from_future(self.export_info_future)
        assert isinstance(export_info, ExportInfo)
        path_in_bucket = self._upload_container(export_info)
        language_definition = LanguageDefinition(
            release_name=self._get_complete_release_name(export_info),
            flavor_path=self.flavor_path,  # type: ignore
            bucketfs_name=self.bucketfs_name,
            bucket_name=self.bucket_name,
            path_in_bucket=self.path_in_bucket,
        )
        language_definitions = language_definition.generate_definition().split(" ")
        language_def_components_list = list()
        for lang_def in language_definitions:
            alias, url = parse_language_definition(lang_def)
            language_def_components_list.append(
                LanguageDefinitionComponents(alias=alias, url=url)
            )

        lang_def_builder = LanguageDefinitionsBuilder(language_def_components_list)
        try:
            release_path = Path(export_info.cache_file).relative_to(Path("").absolute())
        except ValueError:
            release_path = Path(export_info.cache_file)

        result = DeployInfo(
            release_path=str(release_path),
            complete_release_name=self._get_complete_release_name(export_info),
            human_readable_location=self._complete_url(export_info),
            language_definition_builder=lang_def_builder,
            file_extension=detect_container_file_extension(path_in_bucket.name),
        )
        self.return_object(result)

    def build_file_path_in_bucket(self, release_info: ExportInfo) -> bfs.path.PathLike:
        backend = bfs.path.StorageBackend.onprem

        complete_release_name = self._get_complete_release_name(release_info)
        verify = self.ssl_cert_path or self.use_ssl_cert_validation
        path_in_bucket_to_upload_path = bfs.path.build_path(
            backend=backend,
            url=self._url,
            bucket_name=self.bucket_name,
            service_name=self.bucketfs_name,
            username=self.bucketfs_username,
            password=self.bucketfs_password,
            verify=verify,
            path=self.path_in_bucket or "",
        )
        return (
            path_in_bucket_to_upload_path
            / f"{complete_release_name}{detect_container_file_extension(release_info.cache_file)}"
        )

    @property
    def _url(self) -> str:
        return f"{self._get_url_prefix()}{self.database_host}:{self.bucketfs_port}"

    def _complete_url(self, export_info: ExportInfo):
        path_in_bucket = (
            f"{self.path_in_bucket}/" if self.path_in_bucket not in [None, ""] else ""
        )
        return f"{self._url}/{self.bucket_name}/{path_in_bucket}{self._get_complete_release_name(export_info)}{detect_container_file_extension(export_info.cache_file)}"

    def _upload_container(self, release_info: ExportInfo) -> bfs.path.PathLike:
        bucket_path = self.build_file_path_in_bucket(release_info)
        self.logger.info(
            f"Upload {release_info.cache_file} to {self._complete_url(release_info)}"
        )
        with open(release_info.cache_file, "rb") as file:
            bucket_path.write(file)
        return bucket_path

    def _get_complete_release_name(self, release_info: ExportInfo):
        complete_release_name = f"""{release_info.name}-{release_info.release_goal}-{self._get_release_name(
            release_info)}"""
        return complete_release_name

    def _get_release_name(self, release_info: ExportInfo):
        if self.release_name is None:
            release_name = release_info.hash
        else:
            release_name = self.release_name
        return release_name

    def _get_url_prefix(self):
        if self.bucketfs_https:
            url_prefix = "https://"
        else:
            url_prefix = "http://"
        return url_prefix
