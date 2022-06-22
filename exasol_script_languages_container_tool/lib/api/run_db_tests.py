import json
from typing import Tuple, Optional

from exasol_integration_test_docker_environment.cli.options.test_environment_options import LATEST_DB_VERSION
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask

from exasol_script_languages_container_tool.lib.api.invalid_argument_error import InvalidArgumentError
from exasol_script_languages_container_tool.lib.tasks.test.test_container import TestContainer
from exasol_integration_test_docker_environment.cli.common import import_build_steps, \
    set_docker_repository_config, run_task, set_build_config, generate_root_task
from exasol_integration_test_docker_environment.lib.data.environment_type import EnvironmentType


def run_db_test(flavor_path: Tuple[str, ...],
                release_goal: Tuple[str, ...] = ('release',),
                generic_language_test: Optional[Tuple[str, ...]] = None ,
                test_folder: Optional[Tuple[str, ...]] = None,
                test_file: Optional[Tuple[str, ...]] = None,
                test_language: Tuple[str, ...] = (None,),
                test: Optional[Tuple[str, ...]] = None,
                environment_type: str = 'docker_db',
                max_start_attempts: int = 2,
                docker_db_image_version: str = LATEST_DB_VERSION,
                docker_db_image_name: str = "exasol/docker-db",
                external_exasol_db_host: Optional[str] = None,
                external_exasol_db_port: int = 8563,
                external_exasol_bucketfs_port: int = 6583,
                external_exasol_db_user: Optional[str] = None,
                external_exasol_db_password: Optional[str] = None,
                external_exasol_bucketfs_write_password: Optional[str] = None,
                external_exasol_xmlrpc_host: Optional[str] = None,
                external_exasol_xmlrpc_port: int = 443,
                external_exasol_xmlrpc_user: str = "admin",
                external_exasol_xmlrpc_password: Optional[str] = None,
                external_exasol_xmlrpc_cluster_name: str = "cluster1",
                db_mem_size: str = '2 GiB',
                db_disk_size: str = '2 GiB',
                test_environment_vars: str =  "{}",
                test_log_level: str = 'critical',
                reuse_database: bool = False,
                reuse_database_setup: bool = False,
                reuse_uploaded_container: bool = False,
                reuse_test_container: bool = False,
                reuse_test_environment: bool = False,
                force_rebuild: bool = False,
                force_rebuild_from: Optional[Tuple[str, ...]] = None,
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
                task_dependencies_dot_file: Optional[str] = None,
                create_certificates: bool = False):
    """
    This command runs the integration tests in local docker-db.
    The systems spawns a test environment in which the test are executed.
    After finishing the tests, the test environment gets cleaned up.
    If the stages or the packaged container do not exists locally,
    the system will build, pull or export them before running the tests.
    raises:
        InvalidArgumentError: if arguments are not correct.
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

    if reuse_test_environment:
        reuse_database = True
        reuse_uploaded_container = True
        reuse_test_container = True
        reuse_database_setup = True
    if environment_type == EnvironmentType.external_db.name:
        if external_exasol_db_host is None:
            raise InvalidArgumentError("Commandline parameter --external-exasol-db-host not set")
        if external_exasol_db_port is None:
            raise InvalidArgumentError("Commandline parameter --external-exasol_db-port not set")
        if external_exasol_bucketfs_port is None:
            raise InvalidArgumentError("Commandline parameter --external-exasol-bucketfs-port not set")

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=TestContainer,
                                  flavor_paths=list(flavor_path),
                                  release_goals=list(release_goal),
                                  generic_language_tests=list(generic_language_test),
                                  test_folders=list(test_folder),
                                  test_files=list(test_file),
                                  test_restrictions=list(test),
                                  languages=list(test_language),
                                  mem_size=db_mem_size,
                                  disk_size=db_disk_size,
                                  test_environment_vars=json.loads(test_environment_vars),
                                  test_log_level=test_log_level,
                                  reuse_uploaded_container=reuse_uploaded_container,
                                  environment_type=EnvironmentType[environment_type],
                                  reuse_database_setup=reuse_database_setup,
                                  reuse_test_container=reuse_test_container,
                                  reuse_database=reuse_database,
                                  no_test_container_cleanup_after_success=reuse_test_container,
                                  no_test_container_cleanup_after_failure=reuse_test_container,
                                  no_database_cleanup_after_success=reuse_database,
                                  no_database_cleanup_after_failure=reuse_database,
                                  docker_db_image_name=docker_db_image_name,
                                  docker_db_image_version=docker_db_image_version,
                                  max_start_attempts=max_start_attempts,
                                  external_exasol_db_host=external_exasol_db_host,
                                  external_exasol_db_port=external_exasol_db_port,
                                  external_exasol_bucketfs_port=external_exasol_bucketfs_port,
                                  external_exasol_db_user=external_exasol_db_user,
                                  external_exasol_db_password=external_exasol_db_password,
                                  external_exasol_bucketfs_write_password=external_exasol_bucketfs_write_password,
                                  external_exasol_xmlrpc_host=external_exasol_xmlrpc_host,
                                  external_exasol_xmlrpc_port=external_exasol_xmlrpc_port,
                                  external_exasol_xmlrpc_user=external_exasol_xmlrpc_user,
                                  external_exasol_xmlrpc_password=external_exasol_xmlrpc_password,
                                  external_exasol_xmlrpc_cluster_name=external_exasol_xmlrpc_cluster_name,
                                  create_certificates=create_certificates
                                  )

    success, task = run_task(root_task_generator, workers, task_dependencies_dot_file)
    print("Test Results:")
    if task.command_line_output_target.exists():
        with task.command_line_output_target.open("r") as f:
            print(f.read())
    if not success:
        exit(1)

