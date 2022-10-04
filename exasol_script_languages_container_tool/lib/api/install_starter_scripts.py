from pathlib import Path

from exasol_integration_test_docker_environment.lib.api.common import cli_function

from exasol_script_languages_container_tool.lib.tasks.install_starter_scripts.run_starter_script_installation import \
    run_starter_script_installation


@cli_function
def install_starter_scripts(install_path: str = '.',
                            script_dir: str = 'exaslct_scripts',
                            force_install: bool = False) -> None:
    """"
    This command installs the starter scripts which can be used to run this project automatically
    in an isolated environment.
    """
    inst_path = Path(install_path)
    run_starter_script_installation(inst_path, inst_path / script_dir, force_install)
