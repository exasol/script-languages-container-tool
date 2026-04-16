import click
from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

from exasol.slc import api
from exasol.slc.tool.cli import cli
from exasol.slc.tool.options.flavor_options import single_flavor_options


@cli.command(
    short_help="Generates a .dot dependency graph from a flavor's build_steps.py."
)
@add_options(single_flavor_options)
@click.option(
    "--output-path",
    required=False,
    default=None,
    help="Path where to write the .dot file. Defaults to <flavor-path>/build_steps.dot.",
    type=click.Path(exists=False),
)
def generate_build_steps_dot_graph(
    flavor_path: str,
    output_path: str | None,
):
    """
    Generate a .dot file visualizing the build step dependencies of a flavor.
    """
    api.generate_build_steps_dot_graph(
        flavor_path=flavor_path,
        output_path=output_path,
    )
