from typing import Dict, List, Optional, Tuple

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
from exasol_integration_test_docker_environment.lib.docker.images.image_info import (
    ImageInfo,
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

from exasol.slc.internal.tasks.save.docker_save import DockerSave


@cli_function
def save(
    flavor_path: tuple[str, ...],
    save_directory: Optional[str] = None,
    force_save: bool = False,
    save_all: bool = False,
    goal: tuple[str, ...] = tuple(),
    force_rebuild: bool = False,
    force_rebuild_from: tuple[str, ...] = tuple(),
    force_pull: bool = False,
    output_directory: str = ".build_output",
    temporary_base_directory: str = "/tmp",
    log_build_context_content: bool = False,
    cache_directory: Optional[str] = None,
    build_name: Optional[str] = None,
    source_docker_repository_name: str = "exasol/script-language-container",
    source_docker_tag_prefix: str = "",
    source_docker_username: Optional[str] = None,
    source_docker_password: Optional[str] = None,
    target_docker_repository_name: str = "exasol/script-language-container",
    target_docker_tag_prefix: str = "",
    target_docker_username: Optional[str] = None,
    target_docker_password: Optional[str] = None,
    workers: int = 5,
    task_dependencies_dot_file: Optional[str] = None,
    log_level: Optional[str] = None,
    use_job_specific_log_file: bool = True,
) -> dict[str, list[ImageInfo]]:
    """
    This command saves all stages of the script-language-container flavor to a local directory.
    If the stages do not exists locally, the system will build or pull them before the execution of save.
    :raises api_errors.TaskFailureError: if operation is not successful.
    :return: List of image infos per flavor.
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
            task_class=DockerSave,
            save_path=save_directory,
            force_save=force_save,
            save_all=save_all,
            flavor_paths=list(flavor_path),
            goals=list(goal),
        )

    return run_task(
        root_task_generator,
        workers=workers,
        task_dependencies_dot_file=task_dependencies_dot_file,
        log_level=log_level,
        use_job_specific_log_file=use_job_specific_log_file,
    )
