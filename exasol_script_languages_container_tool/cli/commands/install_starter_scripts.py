from pathlib import Path

import click

from exasol_integration_test_docker_environment.cli.cli import cli
from exasol_script_languages_container_tool.lib.tasks.install_starter_scripts.run_starter_script_installation import \
    run_starter_script_installation


@cli.command(short_help="Install starter scripts.")
@click.option("--install-path", default=".",
            type=click.Path(file_okay=False, dir_okay=True),
            help="Target path where starter scripts will be deployed.")
@click.option("--script-dir", default="exaslct_scripts", type=str,
            help="Subdirectory in install path where starter scripts will be deployed.")
@click.option('--force-install/--no-force-install', default=False,
                 help="Forces installation. No prompts will be shown if files/directories already exists. "
                      "They will be silently overwritten.")
def install_starter_scripts(install_path: Path, script_dir: str, force_install: bool):
    """"
    This command installs the starter scripts which can be used to run this project automatically
    in an isolated environment.
    """
    inst_path = Path(install_path)
    run_starter_script_installation(inst_path, inst_path / script_dir, force_install)
