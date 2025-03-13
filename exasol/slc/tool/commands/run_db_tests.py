from typing import Any, Optional, Tuple

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
from exasol_integration_test_docker_environment.cli.options.test_environment_options import (
    docker_db_options,
    external_db_options,
    test_environment_options,
)
from exasol_integration_test_docker_environment.cli.termination_handler import (
    TerminationHandler,
)
from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

from exasol.slc import api
from exasol.slc.api import api_errors
from exasol.slc.tool.cli import cli
from exasol.slc.tool.options.flavor_options import flavor_options
from exasol.slc.tool.options.goal_options import release_options
from exasol.slc.tool.options.test_container_options import test_container_options


@cli.command(short_help="Runs integration tests.")
@add_options(flavor_options)
@add_options(release_options)
@click.option(
    "--generic-language-test",
    multiple=True,
    type=str,
    help="Specifies for which languages the test runner executes generic language tests."
    "The option can be repeated with different languages. "
    "The test runner will run the generic language test for each language.",
)
@click.option(
    "--test-folder",
    multiple=True,
    type=click.Path(),
    help="Specifies in which directories the test runners looks for test files to execute."
    "The option can be repeated with different directories. "
    "The test runner will run the test files in each of these directories.",
)
@click.option(
    "--test-file",
    multiple=True,
    type=click.Path(),
    help="Specifies in which test-files the test runners should execute."
    "The option can be repeated with different test files. "
    "The test runner will run all specified test files.",
)
@click.option(
    "--test-language",
    multiple=True,
    type=str,
    default=[None],
    help="Specifies with which language the test files get executed."
    "The option can be repeated with different languages. "
    "The test runner will run the test files with all specified languages.",
)
@click.option(
    "--test",
    multiple=True,
    type=str,
    help="Define restriction which tests in the test files should be executed."
    "The option can be repeated with different restrictions. "
    "The test runner will run the test files with all specified restrictions.",
)
@add_options(test_environment_options)
@add_options(docker_db_options)
@add_options(external_db_options)
@click.option(
    "--db-mem-size",
    type=str,
    default="2 GiB",
    show_default=True,
    help="The main memory used by the database. Format <number> <unit>, e.g. 1 GiB."
    " The minimum size is 1 GB, below that the database will not start.",
)
@click.option(
    "--db-disk-size",
    type=str,
    default="2 GiB",
    show_default=True,
    help="The disk size available for the database. Format <number> <unit>, e.g. 1 GiB. The minimum size is 100 MiB."
    "However, the setup creates volume files with at least 2 GB larger size,"
    " because the database needs at least so much more disk.",
)
@click.option(
    "--test-environment-vars",
    type=str,
    default="""{}""",
    show_default=True,
    help="""Specifies the environment variables for the test runner as a json
              in the form of {"<variable_name>":<value>}.""",
)
@click.option(
    "--test-log-level",
    default="critical",
    type=click.Choice(["critical", "error", "warning", "info", "debug"]),
    show_default=True,
)
@click.option(
    "--reuse-database/--no-reuse-database",
    default=False,
    help="Reuse a previous create test-database and "
    "disables the clean up of the test-database to allow reuse later.",
)
@click.option(
    "--reuse-database-setup/--no-reuse-database-setup",
    default=False,
    help="Reuse a previous executed database setup in a reused database",
)
@click.option(
    "--reuse-uploaded-container/--no-reuse-uploaded-container",
    default=False,
    help="Reuse the uploaded script-langauge-container in a reused database.",
)
@click.option(
    "--reuse-test-container/--no-reuse-test-container",
    default=False,
    help="Reuse the test container which is used for test execution.",
)
@click.option(
    "--reuse-test-environment/--no-reuse-test-environment",
    default=False,
    help="Reuse the whole test environment with docker network, test container, "
    "database, database setup and uploaded container",
)
@add_options(test_container_options)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
def run_db_test(
    flavor_path: Tuple[str, ...],
    release_goal: Tuple[str, ...],
    generic_language_test: Tuple[str, ...],
    test_folder: Tuple[str, ...],
    test_file: Tuple[str, ...],
    test_language: Tuple[Optional[str], ...],
    test: Tuple[str, ...],
    environment_type: str,
    max_start_attempts: int,
    docker_db_image_version: str,
    docker_db_image_name: str,
    db_os_access: str,
    create_certificates: bool,
    additional_db_parameter: Tuple[str, ...],
    external_exasol_db_host: Optional[str],
    external_exasol_db_port: int,
    external_exasol_bucketfs_port: int,
    external_exasol_ssh_port: Optional[int],
    external_exasol_db_user: Optional[str],
    external_exasol_db_password: Optional[str],
    external_exasol_bucketfs_write_password: Optional[str],
    external_exasol_xmlrpc_host: Optional[str],
    external_exasol_xmlrpc_port: int,
    external_exasol_xmlrpc_user: str,
    external_exasol_xmlrpc_password: Optional[str],
    external_exasol_xmlrpc_cluster_name: str,
    db_mem_size: str,
    db_disk_size: str,
    test_environment_vars: str,
    test_log_level: str,
    reuse_database: bool,
    reuse_database_setup: bool,
    reuse_uploaded_container: bool,
    reuse_test_container: bool,
    reuse_test_environment: bool,
    test_container_folder: str,
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
):
    """
    This command runs the integration tests in local docker-db.
    The system spawns a test environment in which the test are executed.
    After finishing the tests, the test environment gets cleaned up.
    If the stages or the packaged container do not exists locally,
    the system will build, pull or export them before running the tests.
    """
    with TerminationHandler():
        try:
            result = api.run_db_test(
                flavor_path=flavor_path,
                release_goal=release_goal,
                generic_language_test=generic_language_test,
                test_folder=test_folder,
                test_file=test_file,
                test_language=test_language,
                test=test,
                environment_type=environment_type,
                max_start_attempts=max_start_attempts,
                docker_db_image_version=docker_db_image_version,
                docker_db_image_name=docker_db_image_name,
                db_os_access=db_os_access,
                create_certificates=create_certificates,
                additional_db_parameter=additional_db_parameter,
                external_exasol_db_host=external_exasol_db_host,
                external_exasol_db_port=external_exasol_db_port,
                external_exasol_bucketfs_port=external_exasol_bucketfs_port,
                external_exasol_db_user=external_exasol_db_user,
                external_exasol_db_password=external_exasol_db_password,
                external_exasol_ssh_port=external_exasol_ssh_port,
                external_exasol_bucketfs_write_password=external_exasol_bucketfs_write_password,
                external_exasol_xmlrpc_host=external_exasol_xmlrpc_host,
                external_exasol_xmlrpc_port=external_exasol_xmlrpc_port,
                external_exasol_xmlrpc_user=external_exasol_xmlrpc_user,
                external_exasol_xmlrpc_password=external_exasol_xmlrpc_password,
                external_exasol_xmlrpc_cluster_name=external_exasol_xmlrpc_cluster_name,
                db_mem_size=db_mem_size,
                db_disk_size=db_disk_size,
                test_environment_vars=test_environment_vars,
                test_log_level=test_log_level,
                reuse_database=reuse_database,
                reuse_database_setup=reuse_database_setup,
                reuse_uploaded_container=reuse_uploaded_container,
                reuse_test_container=reuse_test_container,
                reuse_test_environment=reuse_test_environment,
                test_container_folder=test_container_folder,
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
            if result.command_line_output_path.exists():
                with result.command_line_output_path.open("r") as f:
                    print(f.read())
            if not result.tests_are_ok:
                raise RuntimeError("Some tests failed")
        except api_errors.MissingArgumentError as e:
            handle_missing_argument_error(e.args)


def handle_missing_argument_error(missing_arguments: Tuple[Any, ...]):
    for e in missing_arguments:
        formatted = f"--{e}".replace("_", "-")
        print(f"Commandline parameter {formatted} not set")
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    exit(1)
