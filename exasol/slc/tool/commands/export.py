from typing import Optional, Tuple

import click
from exasol_integration_test_docker_environment.cli.options.build_options import (
    build_options,
)
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import (
    docker_repository_options,
)
from exasol_integration_test_docker_environment.cli.options.system_options import (
    luigi_logging_options,
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
from exasol.slc.tool.options.goal_options import release_options


@cli.command(short_help="Exports the script-language-container.")
@add_options(flavor_options)
@add_options(release_options)
@click.option(
    "--export-path",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default=None,
    help="The directory where the container file will be stored. If this parameter is omitted, only the cached"
    " file will be created.",
)
@click.option("--release-name", type=str, default=None)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
@click.option(
    "--cleanup-docker-images/--no-cleanup-docker-images",
    default=False,
    help="Clean up the docker images during the export."
    " This might be helpful to save disk space for large containers.",
)
def export(
    flavor_path: Tuple[str, ...],
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
    task_dependencies_dot_file: Optional[str],
    log_level: Optional[str],
    use_job_specific_log_file: bool,
    cleanup_docker_images: bool,
):
    """
    This command exports the whole script-language-container package of the flavor,
    ready for the upload into the bucketfs. If the stages do not exists locally,
    the system will build or pull them before the exporting the packaged container.
    """
    with TerminationHandler():
        export_result = api.export(
            flavor_path=flavor_path,
            release_goal=release_goal,
            export_path=export_path,
            release_name=release_name,
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
            task_dependencies_dot_file=task_dependencies_dot_file,
            log_level=log_level,
            use_job_specific_log_file=use_job_specific_log_file,
            cleanup_docker_images=cleanup_docker_images,
        )
        with open(export_result.command_line_output_path) as f:
            print(f.read())
