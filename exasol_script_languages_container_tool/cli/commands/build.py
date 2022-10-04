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


@cli.command(short_help="Builds a script-languages-container.")
@add_options(flavor_options)
@add_options(goal_options)
@add_options(build_options)
@click.option('--shortcut-build/--no-shortcut-build', default=True,
              help="Forces the system to complete to build all all stages, "
                   "but not to rebuild them. If the target images are locally available "
                   "they will be used as is. If the source images locally available "
                   "they will be taged with target image name. "
                   "If the source images can be loaded from file or pulled from a docker registry "
                   "they will get loaded or pulled. The only case, in which them get builded is "
                   "when they are not otherwise available. "
                   "This includes the case where a higher stage which transitivily "
                   "depends on a images is somewhere available, "
                   "but the images as self is not available.")
@add_options(docker_repository_options)
@add_options(system_options)
def build(flavor_path: Tuple[str, ...],
          goal: Tuple[str, ...],
          force_rebuild: bool,
          force_rebuild_from: Tuple[str, ...],
          force_pull: bool,
          output_directory: str,
          temporary_base_directory: str,
          log_build_context_content: bool,
          cache_directory: Optional[str],
          build_name: Optional[str],
          shortcut_build: bool,
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
    This command builds all stages of the script-language-container flavor.
    If stages are cached in a docker registry, this command is going to pull them,
    instead of building them.
    """
    with TerminationHandler():
        api.build(flavor_path,
                  goal,
                  force_rebuild,
                  force_rebuild_from,
                  force_pull,
                  output_directory,
                  temporary_base_directory,
                  log_build_context_content,
                  cache_directory,
                  build_name,
                  shortcut_build,
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
