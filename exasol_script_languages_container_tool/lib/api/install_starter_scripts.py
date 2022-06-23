from pathlib import Path

from exasol_script_languages_container_tool.lib.tasks.install_starter_scripts.run_starter_script_installation import \
    run_starter_script_installation


def install_starter_scripts(install_path: str = '.',
                            script_dir: str = 'exaslct_scripts',
                            force_install: bool = False):
    """"
    This command installs the starter scripts which can be used to run this project automatically
    in an isolated environment.
    """
    inst_path = Path(install_path)
    run_starter_script_installation(inst_path, inst_path / script_dir, force_install)
