from typing import Tuple, Optional

import click
from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.options.build_options import build_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import system_options
from exasol_integration_test_docker_environment.cli.termination_handler import TerminationHandler
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.cli.options.goal_options import release_options
from exasol_script_languages_container_tool.lib import api


@cli.command(short_help="Exports the script-language-container.")
@add_options(flavor_options)
@add_options(release_options)
@click.option('--export-path', type=click.Path(exists=False, file_okay=False, dir_okay=True), default=None)
@click.option('--release-name', type=str, default=None)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
def export(flavor_path: Tuple[str, ...],
           release_goal: Tuple[str, ...],
           export_path: Optional[str],
           release_name: Optional[str],
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
    This command exports the whole script-language-container package of the flavor,
    ready for the upload into the bucketfs. If the stages do not exists locally,
    the system will build or pull them before the exporting the packaged container.
    """
    with TerminationHandler():
        export_result = api.export(flavor_path,
                                   release_goal,
                                   export_path,
                                   release_name,
                                   force_rebuild,
                                   force_rebuild_from,
                                   force_pull,
                                   output_directory,
                                   temporary_base_directory,
                                   log_build_context_content,
                                   cache_directory,
                                   build_name,
                                   source_docker_repository_name,
                                   source_docker_tag_prefix,
                                   source_docker_username,
                                   source_docker_password,
                                   target_docker_repository_name,
                                   target_docker_tag_prefix,
                                   target_docker_username,
                                   target_docker_password,
                                   workers,
                                   task_dependencies_dot_file)
        with open(export_result.command_line_output_path, "r") as f:
            print(f.read())
