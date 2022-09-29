import getpass
from typing import Tuple, Optional

import luigi
from exasol_integration_test_docker_environment.lib.api.common import import_build_steps, set_build_config, \
    set_docker_repository_config, generate_root_task, run_task, cli_function
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask

from exasol_script_languages_container_tool.lib.tasks.upload.upload_containers import UploadContainers


@cli_function
def upload(flavor_path: Tuple[str, ...],
           database_host: str,
           bucketfs_port: int,
           bucketfs_username: str,
           bucketfs_name: str,
           bucket_name: str,
           bucketfs_password: Optional[str] = None,
           bucketfs_https: bool = False,
           path_in_bucket: str = '',
           release_goal: Tuple[str, ...] = ('release',),
           release_name: Optional[str] = None,
           force_rebuild: bool = False,
           force_rebuild_from: Tuple[str, ...] = tuple(),
           force_pull: bool = False,
           output_directory: str = ".build_output",
           temporary_base_directory: str = "/tmp",
           log_build_context_content: bool = False,
           cache_directory: Optional[str] = None,
           build_name: Optional[str] = None,
           source_docker_repository_name: str = 'exasol/script-language-container',
           source_docker_tag_prefix: str = '',
           source_docker_username: Optional[str] = None,
           source_docker_password: Optional[str] = None,
           target_docker_repository_name: str = 'exasol/script-language-container',
           target_docker_tag_prefix: str = '',
           target_docker_username: Optional[str] = None,
           target_docker_password: Optional[str] = None,
           workers: int = 5,
           task_dependencies_dot_file: Optional[str] = None) -> luigi.LocalTarget:
    """
    This command uploads the whole script-language-container package of the flavor to the database.
    If the stages or the packaged container do not exists locally, the system will build, pull or
    export them before the upload.
    :raises api_errors.TaskFailureError: if operation is not successful.
    :return: Path to resulting report file.
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
    if bucketfs_password is None:
        bucketfs_password = getpass.getpass(
            "BucketFS Password for BucketFS %s and User %s:" % (bucketfs_name, bucketfs_username))

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=UploadContainers,
                                  flavor_paths=list(flavor_path),
                                  release_goals=list(release_goal),
                                  database_host=database_host,
                                  bucketfs_port=bucketfs_port,
                                  bucketfs_username=bucketfs_username,
                                  bucketfs_password=bucketfs_password,
                                  bucket_name=bucket_name,
                                  path_in_bucket=path_in_bucket,
                                  bucketfs_https=bucketfs_https,
                                  release_name=release_name,
                                  bucketfs_name=bucketfs_name)

    return run_task(root_task_generator, workers, task_dependencies_dot_file)
