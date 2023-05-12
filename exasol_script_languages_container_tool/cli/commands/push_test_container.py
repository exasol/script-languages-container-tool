from typing import Tuple, Optional

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.options.build_options import build_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import system_options
from exasol_integration_test_docker_environment.cli.termination_handler import TerminationHandler
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.test_container_options import test_container_options
from exasol_script_languages_container_tool.lib import api


@cli.command(short_help="Pushes the test container docker image to the registry.")
@add_options(test_container_options)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
def push_test_container(
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
        task_dependencies_dot_file: Optional[str]):
    """
    Push the test container docker image to the registry.

    The test container is used during tests of the Script-Language-Container.
    """
    with TerminationHandler():
        api.push_test_container(
            test_container_folder=test_container_folder,
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
