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


@cli.command(
    short_help="Uploads the script-language-container to the database. [Deprecated]"
)
@add_options(flavor_options)
@click.option("--database-host", type=str, required=True)
@click.option("--bucketfs-port", type=int, required=True)
@click.option("--bucketfs-username", type=str, required=True)
@click.option("--bucketfs-name", type=str, required=True)
@click.option("--bucket-name", type=str, required=True)
@click.option("--bucketfs-password", type=str)
@click.option("--bucketfs-https/--no-bucketfs-https", default=False)
@click.option("--path-in-bucket", type=str, required=False, default="")
@add_options(release_options)
@click.option("--release-name", type=str, default=None)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
@click.option("--ssl-cert-path", type=str, default="")
@click.option("--use-ssl-cert-validation/--no-use-ssl-cert-validation", default=True)
def upload(
    flavor_path: Tuple[str, ...],
    database_host: str,
    bucketfs_port: int,
    bucketfs_username: str,
    bucketfs_name: str,
    bucket_name: str,
    bucketfs_password: Optional[str],
    bucketfs_https: bool,
    path_in_bucket: str,
    release_goal: Tuple[str, ...],
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
    ssl_cert_path: str,
    use_ssl_cert_validation: bool,
):
    """
    This command uploads the whole script-language-container package of the flavor to the database.
    If the stages or the packaged container do not exists locally, the system will build, pull or
    export them before the upload.
    This function is deprecated. Use `deploy` instead.
    """
    with TerminationHandler():
        result = api.upload(
            flavor_path=flavor_path,
            database_host=database_host,
            bucketfs_port=bucketfs_port,
            bucketfs_username=bucketfs_username,
            bucketfs_name=bucketfs_name,
            bucket_name=bucket_name,
            bucketfs_password=bucketfs_password,
            bucketfs_https=bucketfs_https,
            path_in_bucket=path_in_bucket,
            release_goal=release_goal,
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
            ssl_cert_path=ssl_cert_path,
            use_ssl_cert_validation=use_ssl_cert_validation,
        )
        with result.open("r") as f:
            print(f.read())
