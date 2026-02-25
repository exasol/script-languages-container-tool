from exasol_integration_test_docker_environment.lib.utils.api_function_decorators import (
    cli_function,
)

from exasol.slc.internal.gen_package_diffs.gen_package_diffs import gen_package_diffs


@cli_function
def generate_package_diffs(
    output_package_diff_directory: str,
    current_working_copy_name: str,
    build_step_path_1: str | None = None,
    build_step_path_2: str | None = None,
    compare_to_commit: str | None = None,
) -> None:
    """
    This command generates a package diff Markdown file per build step for all flavors.
    :raises api_errors.TaskFailureError: if operation is not successful.
    """
    gen_package_diffs(
        output_package_diff_directory,
        current_working_copy_name,
        build_step_path_1,
        build_step_path_2,
        compare_to_commit,
    )
