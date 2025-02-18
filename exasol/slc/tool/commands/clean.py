from typing import Optional, Tuple

from exasol_integration_test_docker_environment.cli.options.docker_repository_options import (
    simple_docker_repository_options,
)
from exasol_integration_test_docker_environment.cli.options.system_options import (
    luigi_logging_options,
    output_directory_option,
    system_options,
)
from exasol_integration_test_docker_environment.cli.termination_handler import (
    TerminationHandler,
)
from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

from exasol.slc import api
from exasol.slc.tool.cli import cli
from exasol.slc.tool.options.flavor_options import flavor_options


@cli.command(
    short_help="Cleans script-languages-container docker images for the given flavor."
)
@add_options(flavor_options)
@add_options([output_directory_option])
@add_options(simple_docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
def clean_flavor_images(
    flavor_path: Tuple[str, ...],
    output_directory: str,
    docker_repository_name: str,
    docker_tag_prefix: str,
    workers: int,
    task_dependencies_dot_file: Optional[str],
    log_level: Optional[str],
    use_job_specific_log_file: bool,
):
    """
    This command removes the docker images of all stages of the script languages container for the given flavor.
    """
    with TerminationHandler():
        api.clean_flavor_images(
            flavor_path=flavor_path,
            output_directory=output_directory,
            docker_repository_name=docker_repository_name,
            docker_tag_prefix=docker_tag_prefix,
            workers=workers,
            task_dependencies_dot_file=task_dependencies_dot_file,
            log_level=log_level,
            use_job_specific_log_file=use_job_specific_log_file,
        )


@cli.command(
    short_help="Cleans all script-languages-container docker images for all flavors."
)
@add_options([output_directory_option])
@add_options(simple_docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
def clean_all_images(
    output_directory: str,
    docker_repository_name: str,
    docker_tag_prefix: str,
    workers: int,
    task_dependencies_dot_file: Optional[str],
    log_level: Optional[str],
    use_job_specific_log_file: bool,
):
    """
    This command removes the docker images of all stages of the script languages container for all flavors.
    """
    with TerminationHandler():
        api.clean_all_images(
            output_directory=output_directory,
            docker_repository_name=docker_repository_name,
            docker_tag_prefix=docker_tag_prefix,
            workers=workers,
            task_dependencies_dot_file=task_dependencies_dot_file,
            log_level=log_level,
            use_job_specific_log_file=use_job_specific_log_file,
        )


# TODO add commands clean containers, networks, all
