import sys
from typing import Tuple, Optional

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.common import add_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import \
    simple_docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import output_directory_option, \
    system_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.lib import api
from exasol_script_languages_container_tool.lib.api import api_errors


@cli.command(short_help="Cleans script-languages-container docker images for the given flavor.")
@add_options(flavor_options)
@add_options([output_directory_option])
@add_options(simple_docker_repository_options)
@add_options(system_options)
def clean_flavor_images(flavor_path: Tuple[str, ...],
                        output_directory: str,
                        docker_repository_name: str,
                        docker_tag_prefix: str,
                        workers: int,
                        task_dependencies_dot_file: Optional[str]):
    """
    This command removes the docker images of all stages of the script languages container for the given flavor.
    """
    try:
        api.clean_flavor_images(flavor_path, output_directory, docker_repository_name,
                                docker_tag_prefix, workers, task_dependencies_dot_file)
    except api_errors.TaskFailureError:
        sys.exit(1)


@cli.command(short_help="Cleans all script-languages-container docker images for all flavors.")
@add_options([output_directory_option])
@add_options(simple_docker_repository_options)
@add_options(system_options)
def clean_all_images(
        output_directory: str,
        docker_repository_name: str,
        docker_tag_prefix: str,
        workers: int,
        task_dependencies_dot_file: Optional[str]):
    """
    This command removes the docker images of all stages of the script languages container for all flavors.
    """
    try:
        api.clean_all_images(output_directory, docker_repository_name, docker_tag_prefix,
                             workers, task_dependencies_dot_file)
    except api_errors.TaskFailureError:
        sys.exit(1)

# TODO add commands clean containers, networks, all
