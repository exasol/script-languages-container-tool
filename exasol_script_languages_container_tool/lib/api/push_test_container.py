from typing import Tuple, Optional

from exasol_integration_test_docker_environment.lib import api
from exasol_integration_test_docker_environment.lib.api.common import cli_function
from exasol_integration_test_docker_environment.lib.docker.images.image_info import ImageInfo

from exasol_script_languages_container_tool.cli.options.test_container_options import TEST_CONTAINER_DEFAULT_DIRECTORY
from exasol_script_languages_container_tool.lib.tasks.test.test_container_content import build_test_container_content


@cli_function
def push_test_container(
        test_container_folder: str = TEST_CONTAINER_DEFAULT_DIRECTORY,
        force_rebuild: bool = False,
        force_rebuild_from: Tuple[str, ...] = tuple(),
        force_pull: bool = False,
        output_directory: str = ".build_output",
        temporary_base_directory: str = "/tmp",
        log_build_context_content: bool = False,
        cache_directory: Optional[str] = None,
        build_name: Optional[str] = None,
        source_docker_repository_name: str = 'exasol/script-language-container',
        source_docker_tag_prefix: str = '',
        source_docker_username: Optional[str] = None,
        source_docker_password: Optional[str] = None,
        target_docker_repository_name: str = 'exasol/script-language-container',
        target_docker_tag_prefix: str = '',
        target_docker_username: Optional[str] = None,
        target_docker_password: Optional[str] = None,
        workers: int = 5,
        task_dependencies_dot_file: Optional[str] = None) -> ImageInfo:
    """
    Push the test container docker image to the registry.

    The test container is used during tests of the Script-Language-Container.
    """
    return api.push_test_container(
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
