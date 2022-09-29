from typing import Tuple, Optional

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.options.build_options import build_options
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import system_options
from exasol_integration_test_docker_environment.cli.termination_handler import TerminationHandler
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.lib import api


@cli.command(short_help="Performs a security scan.")
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
    This command executes the security scan, which must be defined as separate step in the build steps declaration.
    The scan runs the docker container of the respective step, passing a folder of the output-dir as argument.
    If the stages do not exists locally, the system will build or pull them before running the scan.
    """
    with TerminationHandler():
        scan_result = api.security_scan(flavor_path,
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
        if scan_result.report_path.exists():
            with scan_result.report_path.open("r") as f:
                print(f.read())
        if not scan_result.scans_are_ok:
            raise RuntimeError("Some security scans not successful.")
