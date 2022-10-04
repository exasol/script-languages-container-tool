from typing import Tuple, Optional

import click
from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.options.build_options import build_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import system_options
from exasol_integration_test_docker_environment.cli.termination_handler import TerminationHandler
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.cli.options.goal_options import goal_options
from exasol_script_languages_container_tool.lib import api


@cli.command(short_help="Saves all stages of a script-language-container flavor.")
@add_options(flavor_options)
@click.option('--save-directory',
              type=click.Path(file_okay=False, dir_okay=True),
              help="Directory where to save the image tarballs")
@click.option('--force-save/--no-force-save', default=False,
              help="Forces the system to overwrite existing save for build steps that run")
@click.option('--save-all/--no-save-all', default=False,
              help="Forces the system to save all images of build-steps that are specified by the goals")
@add_options(goal_options)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
def save(flavor_path: Tuple[str, ...],
         save_directory: Optional[str],
         force_save: bool,
         save_all: bool,
         goal: Tuple[str, ...],
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
    This command saves all stages of the script-language-container flavor to a local directory.
    If the stages do not exists locally, the system will build or pull them before the execution of save.
    """
    with TerminationHandler():
        api.save(flavor_path,
                 save_directory,
                 force_save,
                 save_all,
                 goal,
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
