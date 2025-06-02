from typing import Optional, Tuple

from exasol_integration_test_docker_environment.cli.options.build_options import (
    build_options,
)
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import (
    docker_repository_options,
)
from exasol_integration_test_docker_environment.cli.options.push_options import (
    push_options,
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
from exasol.slc.tool.options.goal_options import goal_options


@cli.command(short_help="Pushes script languages container to docker repository.")
@add_options(flavor_options)
@add_options(goal_options)
@add_options(push_options)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
def push(
    flavor_path: tuple[str, ...],
    goal: tuple[str, ...],
    force_push: bool,
    push_all: bool,
    force_rebuild: bool,
    force_rebuild_from: tuple[str, ...],
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
):
    """
    This command pushes all stages of the script-language-container flavor.
    If the stages do not exists locally, the system will build or pull them before the push.
    """
    with TerminationHandler():
        api.push(
            flavor_path=flavor_path,
            goal=goal,
            force_push=force_push,
            push_all=push_all,
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
        )
