from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import (
    DependencyLoggerBaseTask,
)
from exasol_integration_test_docker_environment.lib.base.import_build_step import (
    import_build_steps,
)
from exasol_integration_test_docker_environment.lib.base.run_task import (
    generate_root_task,
    run_task,
)
from exasol_integration_test_docker_environment.lib.models.config.build_config import (
    set_build_config,
)
from exasol_integration_test_docker_environment.lib.models.config.docker_config import (
    set_docker_repository_config,
)
from exasol_integration_test_docker_environment.lib.utils.api_function_decorators import (
    cli_function,
)

from exasol.slc.internal.tasks.upload.deploy_containers import DeployContainers
from exasol.slc.internal.tasks.upload.deploy_info import toDeployResult
from exasol.slc.models.compression_strategy import (
    CompressionStrategy,
    defaultCompressionStrategy,
)
from exasol.slc.models.deploy_result import DeployResult


@cli_function
def deploy(
    flavor_path: tuple[str, ...],
    bucketfs_host: str | None = None,
    bucketfs_port: int | None = None,
    bucketfs_user: str | None = None,
    bucketfs_name: str | None = None,
    bucket: str | None = None,
    bucketfs_use_https: bool = False,
    bucketfs_password: str | None = None,
    path_in_bucket: str | None = None,
    saas_host: str | None = None,
    saas_pat: str | None = None,
    saas_database_id: str | None = None,
    saas_database_name: str | None = None,
    saas_account_id: str | None = None,
    ssl_cert_path: str | None = None,
    use_ssl_cert_validation: bool = True,
    release_goal: tuple[str, ...] = ("release",),
    release_name: str | None = None,
    force_rebuild: bool = False,
    force_rebuild_from: tuple[str, ...] = tuple(),
    force_pull: bool = False,
    output_directory: str = ".build_output",
    temporary_base_directory: str = "/var/tmp",
    log_build_context_content: bool = False,
    cache_directory: str | None = None,
    build_name: str | None = None,
    source_docker_repository_name: str = "exasol/script-language-container",
    source_docker_tag_prefix: str = "",
    source_docker_username: str | None = None,
    source_docker_password: str | None = None,
    target_docker_repository_name: str = "exasol/script-language-container",
    target_docker_tag_prefix: str = "",
    target_docker_username: str | None = None,
    target_docker_password: str | None = None,
    workers: int = 5,
    task_dependencies_dot_file: str | None = None,
    log_level: str | None = None,
    use_job_specific_log_file: bool = True,
    compression_strategy: CompressionStrategy = defaultCompressionStrategy(),
) -> dict[str, dict[str, DeployResult]]:
    """
    This command uploads the whole script-language-container package of the flavor to the database.
    If the stages or the packaged container do not exist locally, the system will build, pull or
    export them before the upload.
    :raises api_errors.TaskFailureError: if operation is not successful.
    :return: A dictionary with an instance of class DeployResult for each release for each deployed flavor.
    For example { "flavors/standard-flavor" : {"release" : DeployResult(...) } }
    """
    import_build_steps(flavor_path)
    set_build_config(
        force_rebuild,
        force_rebuild_from,
        force_pull,
        log_build_context_content,
        output_directory,
        temporary_base_directory,
        cache_directory,
        build_name,
    )
    set_docker_repository_config(
        source_docker_password,
        source_docker_repository_name,
        source_docker_username,
        source_docker_tag_prefix,
        "source",
    )
    set_docker_repository_config(
        target_docker_password,
        target_docker_repository_name,
        target_docker_username,
        target_docker_tag_prefix,
        "target",
    )

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(
            task_class=DeployContainers,
            flavor_paths=list(flavor_path),
            release_goals=list(release_goal),
            database_host=bucketfs_host,
            bucketfs_port=str(bucketfs_port) if bucketfs_port else None,
            bucketfs_username=bucketfs_user,
            bucketfs_password=bucketfs_password,
            bucket_name=bucket,
            path_in_bucket=path_in_bucket,
            bucketfs_https=bucketfs_use_https,
            release_name=release_name,
            bucketfs_name=bucketfs_name,
            ssl_cert_path=ssl_cert_path,
            use_ssl_cert_validation=use_ssl_cert_validation,
            compression_strategy=compression_strategy,
            saas_host=saas_host,
            saas_pat=saas_pat,
            saas_account_id=saas_account_id,
            saas_database_id=saas_database_id,
            saas_database_name=saas_database_name,
        )

    deploy_infos = run_task(
        root_task_generator,
        workers=workers,
        task_dependencies_dot_file=task_dependencies_dot_file,
        log_level=log_level,
        use_job_specific_log_file=use_job_specific_log_file,
    )

    return {
        flavor: {
            release: toDeployResult(
                deploy_info=deploy_info,
                bucketfs_use_https=bucketfs_use_https,
                bucketfs_host=bucketfs_host,
                bucketfs_port=bucketfs_port,
                bucket_name=bucket,
                bucketfs_name=bucketfs_name,
                bucketfs_username=bucketfs_user,
                bucketfs_password=bucketfs_password,
                ssl_cert_path=ssl_cert_path,
                use_ssl_cert_validation=use_ssl_cert_validation,
                path_in_bucket=path_in_bucket,
                saas_token=saas_pat,
                saas_account_id=saas_account_id,
                saas_database_id=saas_database_id,
                saas_database_name=saas_database_name,
                saas_url=saas_host,
            )
            for release, deploy_info in deploy_info_per_release.items()
        }
        for flavor, deploy_info_per_release in deploy_infos.items()
    }
