import os
from enum import Enum
from typing import Any, Optional, Tuple

import click
from exasol_integration_test_docker_environment.cli.cli import cli  # type: ignore
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
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.flavor_options import (
    flavor_options,
)
from exasol_script_languages_container_tool.cli.options.goal_options import (
    release_options,
)
from exasol_script_languages_container_tool.lib import api

# This text will be displayed instead of the actual value, if found in an environment
# variable, in a prompt.
SECRET_DISPLAY = "***"


class SecretParams(Enum):
    """
    This enum serves as a definition of confidential parameters which values should not be
    displayed in the console, unless the user types them in the command line.

    The enum name is also the name of the environment variable where the correspondent
    secret value can be stored.

    The enum value is also the name of the cli parameter.
    """

    DB_PASSWORD = "db-pass"
    BUCKETFS_PASSWORD = "bucketfs-password"


def secret_callback(ctx: click.Context, param: click.Option, value: Any):
    """
    Here we try to get the secret parameter value from an environment variable.
    The reason for doing this in the callback instead of using a callable default is
    that we don't want the default to be displayed in the prompt. There seems to
    be no way of altering this behaviour.
    """
    if value == SECRET_DISPLAY:
        secret_param = SecretParams(param.opts[0][2:])
        return os.environ.get(secret_param.name)
    return value


@cli.command(short_help="Deploys the script-language-container in the database.")
@add_options(flavor_options)
@click.option("--bucketfs-host", type=str, required=True)
@click.option("--bucketfs-port", type=int, required=True)
@click.option("--bucketfs-use-https", type=bool, default=False)
@click.option("--bucketfs-user", type=str)
@click.option("--bucketfs-name", type=str, required=True)
@click.option("--bucket", type=str)
@click.option(
    f"--{SecretParams.BUCKETFS_PASSWORD.value}",
    type=str,
    prompt="BucketFS password",
    prompt_required=False,
    hide_input=True,
    default=SECRET_DISPLAY,
    callback=secret_callback,
)
@click.option("--path-in-bucket", type=str, required=False, default="")
@add_options(release_options)
@click.option("--release-name", type=str, default=None)
@add_options(build_options)
@add_options(docker_repository_options)
@add_options(system_options)
@add_options(luigi_logging_options)
@click.option("--ssl-cert-path", type=str, default="")
@click.option("--use-ssl-cert-validation/--no-use-ssl-cert-validation", default=True)
def deploy(
    flavor_path: Tuple[str, ...],
    bucketfs_host: str,
    bucketfs_port: int,
    bucketfs_use_https: str,
    bucketfs_user: str,
    bucketfs_name: str,
    bucket: str,
    bucketfs_password: str,
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
    """
    with TerminationHandler():
        result = api.deploy(
            flavor_path=flavor_path,
            bucketfs_host=bucketfs_host,
            bucketfs_port=bucketfs_port,
            bucketfs_user=bucketfs_user,
            bucketfs_name=bucketfs_name,
            bucket=bucket,
            bucketfs_password=bucketfs_password,
            bucketfs_use_https=bucketfs_use_https,
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
