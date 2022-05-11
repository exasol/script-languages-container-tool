from typing import Tuple

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.cli.common import add_options, set_output_directory, \
    set_docker_repository_config, generate_root_task, run_task, import_build_steps
from exasol_integration_test_docker_environment.cli.options.docker_repository_options import \
    simple_docker_repository_options
from exasol_integration_test_docker_environment.cli.options.system_options import output_directory_option, \
    system_options
from exasol_integration_test_docker_environment.lib.base.dependency_logger_base_task import DependencyLoggerBaseTask

from exasol_script_languages_container_tool.cli.options.flavor_options import flavor_options
from exasol_script_languages_container_tool.lib.tasks.clean.clean_images import CleanExaslcAllImages, \
    CleanExaslcFlavorsImages


@cli.command(short_help="Cleans script-languages-container docker images for the given flavor.")
@add_options(flavor_options)
@add_options([output_directory_option])
@add_options(simple_docker_repository_options)
@add_options(system_options)
def clean_flavor_images(flavor_path: Tuple[str, ...],
                        output_directory: str,
                        docker_repository_name: str,
                        docker_tag_prefix: str,
                        workers: int,
                        task_dependencies_dot_file: str):
    """
    This command removes the docker images of all stages of the script languages container for the given flavor.
    """
    import_build_steps(flavor_path)
    set_output_directory(output_directory)
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "source")
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "target")

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=CleanExaslcFlavorsImages, flavor_paths=list(flavor_path))

    success, task = run_task(root_task_generator, workers, task_dependencies_dot_file)
    if not success:
        exit(1)


@cli.command(short_help="Cleans all script-languages-container docker images for all flavors.")
@add_options([output_directory_option])
@add_options(simple_docker_repository_options)
@add_options(system_options)
def clean_all_images(
        output_directory: str,
        docker_repository_name: str,
        docker_tag_prefix: str,
        workers: int,
        task_dependencies_dot_file: str):
    """
    This command removes the docker images of all stages of the script languages container for all flavors.
    """
    set_output_directory(output_directory)
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "source")
    set_docker_repository_config(None, docker_repository_name, None, docker_tag_prefix, "target")

    def root_task_generator() -> DependencyLoggerBaseTask:
        return generate_root_task(task_class=CleanExaslcAllImages)

    success, task = run_task(root_task_generator, workers, task_dependencies_dot_file)
    if not success:
        exit(1)

# TODO add commands clean containers, networks, all
