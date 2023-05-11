from typing import Tuple, Optional

from exasol_integration_test_docker_environment.lib import api
from exasol_integration_test_docker_environment.lib.api.common import cli_function
from exasol_integration_test_docker_environment.lib.docker.images.image_info import ImageInfo

from exasol_script_languages_container_tool.lib.tasks.test.test_container_content import build_test_container_content

@cli_function
def build_test_container(
        test_container_folder: str,
        force_rebuild: bool,
        force_rebuild_from: Tuple[str, ...],
        force_pull: bool,
        output_directory: str,
        temporary_base_directory: str,
        log_build_context_content: bool,
        cache_directory: Optional[str],
        build_name: Optional[str],
        source_docker_repository_name: str,
        source_docker_tag_prefix: str,
        source_docker_username: Optional[str],
        source_docker_password: Optional[str],
        target_docker_repository_name: str,
        target_docker_tag_prefix: str,
        target_docker_username: Optional[str],
        target_docker_password: Optional[str],
        workers: int,
        task_dependencies_dot_file: Optional[str]) -> ImageInfo:
    """
    Build the test container docker image.

    The test container is used during tests of the Script-Language-Container.
    """
    return api.build_test_container(
        test_container_content=build_test_container_content(test_container_folder),
        force_rebuild=force_rebuild,
        force_rebuild_from=force_rebuild_from,
        force_pull=force_pull,
        output_directory=output_directory,
        temporary_base_directory=temporary_base_directory,
        log_build_context_content=log_build_context_content,
        cache_directory=cache_directory,
        build_name=build_name,
        source_docker_repository_name=source_docker_repository_name,
        source_docker_tag_prefix=source_docker_tag_prefix,
        source_docker_username=source_docker_username,
        source_docker_password=source_docker_password,
        target_docker_repository_name=target_docker_repository_name,
        target_docker_tag_prefix=target_docker_tag_prefix,
        target_docker_username=target_docker_username,
        target_docker_password=target_docker_password,
        workers=workers,
        task_dependencies_dot_file=task_dependencies_dot_file)
