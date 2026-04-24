from exasol_integration_test_docker_environment.lib.utils.api_function_decorators import (
    cli_function,
)

from exasol.slc.internal.generate_build_steps_dot_graph import generate_dot


@cli_function
def generate_build_steps_dot_graph(
    flavor_path: str,
    output_path: str | None = None,
) -> str:
    """
    Generate a .dot dependency graph from a flavor's build_steps.py.

    :param flavor_path: Path to the flavor directory.
    :param output_path: Optional path where to write the .dot file.
    :return: The .dot file content as a string.
    :raises FileNotFoundError: if build_steps.py not found in the flavor.
    """
    return generate_dot(
        flavor_path=flavor_path,
        output_path=output_path,
    )
