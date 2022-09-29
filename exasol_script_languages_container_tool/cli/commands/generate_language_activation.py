import click
from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_integration_test_docker_environment.lib.api.common import add_options

from exasol_script_languages_container_tool.cli.options.flavor_options import single_flavor_options
from exasol_script_languages_container_tool.lib import api


@cli.command(short_help="Generate the language activation statement.")
@add_options(single_flavor_options)
@click.option('--bucketfs-name', type=str, required=True)
@click.option('--bucket-name', type=str, required=True)
@click.option('--container-name', type=str, required=True)
@click.option('--path-in-bucket', type=str, required=False, default="")
def generate_language_activation(
        flavor_path: str,
        bucketfs_name: str,
        bucket_name: str,
        container_name: str,
        path_in_bucket: str):
    """
    Generate the language activation statement.
    """
    _, _, result = \
        api.generate_language_activation(flavor_path, bucketfs_name, bucket_name, container_name, path_in_bucket)
    print(result)
