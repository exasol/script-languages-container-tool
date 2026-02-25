import click

from exasol.slc import api
from exasol.slc.tool.cli import cli


@cli.command(
    short_help="Generates a package diff Markdown file per build step for all flavors.."
)
@click.option(
    "--output-package-diff-directory",
    required=True,
    help="Directory where the diff reports are generated",
    type=click.Path(exists=False),
)
@click.option(
    "--current-working-copy-name",
    required=True,
    help="Name of the current git working copy. "
    "For example, the version of a new release.",
    type=str,
)
@click.option(
    "--build-step-path-1",
    required=False,
    default=None,
    help="If this is set we only compare this build step with --build-step-path-2.",
    type=click.Path(exists=True),
)
@click.option(
    "--build-step-path-2",
    required=False,
    default=None,
    help="If this is set we only compare this build step with --build-step-path-1.",
    type=click.Path(exists=True),
)
@click.option(
    "--compare-to-commit",
    required=False,
    help="Commit to compare to.",
    default=None,
    type=str,
)
def generate_package_diffs(
    output_package_diff_directory: str,
    current_working_copy_name: str,
    build_step_path_1: str | None,
    build_step_path_2: str | None,
    compare_to_commit: str | None,
):
    """
    This command generates a package diff Markdown file per build step for all flavors.
    """
    api.generate_package_diffs(
        output_package_diff_directory=output_package_diff_directory,
        current_working_copy_name=current_working_copy_name,
        build_step_path_1=build_step_path_1,
        build_step_path_2=build_step_path_2,
        compare_to_commit=compare_to_commit,
    )
