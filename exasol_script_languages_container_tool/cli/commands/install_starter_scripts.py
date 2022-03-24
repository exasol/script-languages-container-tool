from pathlib import Path

import click

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_script_languages_container_tool.lib.tasks.install_starter_scripts.run_starter_script_installation import \
    run_starter_script_installation


@cli.command()
@click.option("--install-path", default=".",
            type=click.Path(file_okay=False, dir_okay=True),
            help="Target path where starter scripts will be deployed.")
@click.option("--script-dir", default="exaslct_scripts", type=str,
            help="Subdirectory in install path where starter scripts will be deployed.")
def install_starter_scripts(install_path: Path, script_dir: str):
    inst_path = Path(install_path)
    run_starter_script_installation(inst_path, inst_path / script_dir)
