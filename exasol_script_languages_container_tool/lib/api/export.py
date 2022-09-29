from typing import Tuple, Optional

from exasol_integration_test_docker_environment.lib.api.common import import_build_steps, set_build_config, \
    set_docker_repository_config, generate_root_task, run_task, cli_function
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask

from exasol_script_languages_container_tool.lib.tasks.export.export_containers import ExportContainers, \
    ExportContainerResult


@cli_function
def export(flavor_path: Tuple[str, ...],
           release_goal: Tuple[str, ...] = ('release',),
           export_path: Optional[str] = None,
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
           task_dependencies_dot_file: Optional[str] = None) -> ExportContainerResult:
    """
    This command exports the whole script-language-container package of the flavor,
    ready for the upload into the bucketfs. If the stages do not exists locally,
    the system will build or pull them before the exporting the packaged container.
    :raises api_errors.TaskFailureError: if operation is not successful.
    :returns: ExportContainerResult
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

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=ExportContainers,
                                  flavor_paths=list(flavor_path),
                                  release_goals=list(release_goal),
                                  export_path=export_path,
                                  release_name=release_name)

    return run_task(root_task_generator, workers, task_dependencies_dot_file)
