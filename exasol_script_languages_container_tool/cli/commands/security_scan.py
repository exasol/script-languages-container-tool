from pathlib import Path
from typing import Tuple

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.common import add_options, import_build_steps, set_build_config, \
    set_docker_repository_config, generate_root_task, run_task
from exasol_integration_test_docker_environment.cli.options.build_options import build_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import system_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.lib.tasks.security_scan.security_scan import SecurityScan
from exasol_script_languages_container_tool.lib.utils.logging_redirection import log_redirector_task_creator_wrapper


@cli.command()
@add_options(flavor_options)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
def security_scan(flavor_path: Tuple[str, ...],
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
    This command executes the security scan, which must be defined as separate step in the build steps declaration.
    The scan runs the docker container of the respective step, passing a folder of the output-dir as argument.
    If the stages do not exists locally, the system will build or pull them before running the scan.
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

    report_path = Path(output_directory).joinpath("security_scan")
    with log_redirector_task_creator_wrapper(lambda: generate_root_task(task_class=SecurityScan,
                                                                        flavor_paths=list(flavor_path),
                                                                        report_path=str(report_path)
                                                                        )) as task_creator:
        success, task = run_task(task_creator, workers, task_dependencies_dot_file)

        if success:
            with task.security_report_target.open("r") as f:
                print(f.read())

    if not success:
        exit(1)
