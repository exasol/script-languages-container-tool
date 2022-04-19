from typing import Tuple

import click
from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.common import add_options, import_build_steps, set_build_config, \
    set_docker_repository_config, generate_root_task, run_task
from exasol_integration_test_docker_environment.cli.options.build_options import build_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import system_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.cli.options.goal_options import release_options
from exasol_script_languages_container_tool.lib.tasks.export.export_containers import ExportContainers
from exasol_script_languages_container_tool.lib.utils.logging_redirection import log_redirector_task_creator_wrapper


@cli.command()
@add_options(flavor_options)
@add_options(release_options)
@click.option('--export-path', type=click.Path(exists=False, file_okay=False, dir_okay=True), default=None)
@click.option('--release-name', type=str, default=None)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
def export(flavor_path: Tuple[str, ...],
           release_goal: Tuple[str, ...],
           export_path: str,
           release_name: str,
           force_rebuild: bool,
           force_rebuild_from: Tuple[str, ...],
           force_pull: bool,
           output_directory: str,
           temporary_base_directory: str,
           log_build_context_content: bool,
           cache_directory: str,
           build_name: str,
           source_docker_repository_name: str,
           source_docker_tag_prefix: str,
           source_docker_username: str,
           source_docker_password: str,
           target_docker_repository_name: str,
           target_docker_tag_prefix: str,
           target_docker_username: str,
           target_docker_password: str,
           workers: int,
           task_dependencies_dot_file: str):
    """
    This command exports the whole script language container package of the flavor,
    ready for the upload into the bucketfs. If the stages do not exists locally,
    the system will build or pull them before the exporting the packaged container.
    """
    import_build_steps(flavor_path)
    set_build_config(force_rebuild,
                     force_rebuild_from,
                     force_pull,
                     log_build_context_content,
                     output_directory,
                     temporary_base_directory,
                     cache_directory,
                     build_name)
    set_docker_repository_config(source_docker_password, source_docker_repository_name, source_docker_username,
                                 source_docker_tag_prefix, "source")
    set_docker_repository_config(target_docker_password, target_docker_repository_name, target_docker_username,
                                 target_docker_tag_prefix, "target")

    with log_redirector_task_creator_wrapper(lambda: generate_root_task(task_class=ExportContainers,
                                                                                  flavor_paths=list(flavor_path),
                                                                                  release_goals=list(release_goal),
                                                                                  export_path=export_path,
                                                                                  release_name=release_name
                                                                                  )) as task_creator:

        success, task = run_task(task_creator, workers, task_dependencies_dot_file)
        if success:
            with task.command_line_output_target.open("r") as f:
                print(f.read())

    if not success:
        exit(1)
