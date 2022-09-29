from typing import Tuple, Optional

from exasol_integration_test_docker_environment.lib.api.common import run_task, generate_root_task, \
    set_output_directory, set_docker_repository_config, import_build_steps, cli_function
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask

from exasol_script_languages_container_tool.lib.tasks.clean.clean_images import CleanExaslcAllImages, \
    CleanExaslcFlavorsImages


@cli_function
def clean_flavor_images(flavor_path: Tuple[str, ...],
                        output_directory: str = ".build_output",
                        docker_repository_name: str = 'exasol/script-language-container',
                        docker_tag_prefix: str = '',
                        workers: int = 5,
                        task_dependencies_dot_file: Optional[str] = None) -> None:
    """
    This command removes the docker images of all stages of the script languages container for the given flavor.
    raises:
        api_errors.TaskFailureError: if operation is not successful.
    """
    import_build_steps(flavor_path)
    set_output_directory(output_directory)
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "source")
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "target")

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=CleanExaslcFlavorsImages, flavor_paths=list(flavor_path))

    run_task(root_task_generator, workers, task_dependencies_dot_file)


@cli_function
def clean_all_images(
        output_directory: str = '.build_output',
        docker_repository_name: str = 'exasol/script-language-container',
        docker_tag_prefix: str = '',
        workers: int = 5,
        task_dependencies_dot_file: Optional[str] = None) -> None:
    """
    This command removes the docker images of all stages of the script languages container for all flavors.
    raises:
        api_errors.TaskFailureError: if operation is not successful.
    """
    set_output_directory(output_directory)
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "source")
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "target")

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=CleanExaslcAllImages)

    run_task(root_task_generator, workers, task_dependencies_dot_file)

# TODO add commands clean containers, networks, all
