from typing import Tuple, Optional

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import \
    simple_docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import output_directory_option, \
    system_options
from exasol_integration_test_docker_environment.cli.termination_handler import TerminationHandler
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.lib import api


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
    with TerminationHandler():
        api.clean_flavor_images(flavor_path, output_directory, docker_repository_name,
                                docker_tag_prefix, workers, task_dependencies_dot_file)


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
    with TerminationHandler():
        api.clean_all_images(output_directory, docker_repository_name, docker_tag_prefix,
                             workers, task_dependencies_dot_file)

# TODO add commands clean containers, networks, all
