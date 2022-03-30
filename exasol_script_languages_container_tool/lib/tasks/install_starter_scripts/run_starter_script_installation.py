import os
import shutil
import sys
from pathlib import Path
import importlib_metadata
import importlib_resources

EXASLCT_INSTALL_DIRECTORY = "exaslct_scripts"
PACKAGE_IDENTITY = "exasol-script-languages-container-tool"
MODULE_IDENTITY = PACKAGE_IDENTITY.replace("-", "_")


def run_starter_script_installation(install_path: Path, target_script_path: Path, force_install: bool):
    print(f"Installing to {install_path}")
    if target_script_path.exists() and not force_install:
        print(f"The installation directory for exaslct at {install_path} already exists.")
        print("Do you want to remove it and continue with installation?")

        answer = input("yes/no: ")
        if answer == "yes":
            shutil.rmtree(target_script_path)
        else:
            print("Can't continue with the installation, because the installation directory already exists.")
            sys.exit(1)
    elif force_install:
        shutil.rmtree(target_script_path)

    version = importlib_metadata.version(MODULE_IDENTITY)

    print(f"Found version: {version}")
    target_script_path.mkdir(parents=True)
    starter_script_dir = importlib_resources.files(MODULE_IDENTITY) / "starter_scripts"
    print(f"starter_script_dir is {starter_script_dir}")
    for script in starter_script_dir.iterdir():
        with importlib_resources.as_file(script) as script_file:
            print(f"Copying {script_file} to {target_script_path / script_file.name}")
            shutil.copyfile(script_file,  target_script_path / script_file.name)

    exaslct_script_path = importlib_resources.files(MODULE_IDENTITY) / "starter_scripts/exaslct_install_template.sh"
    exaslct_script = exaslct_script_path.read_text()
    exaslct_script = exaslct_script.replace("<<<<EXASLCT_GIT_REF>>>>", version)

    with open(target_script_path / "exaslct.sh", "w") as exaslct_file:
        exaslct_file.write(exaslct_script)

    os.chmod(target_script_path / "exaslct.sh", 0o0764) #Full access (rwx) for owner, for group only r/w access, readonly fo rall others

    exaslct_symlink_path = install_path / "exaslct"

    exaslct_symlin_exists = exaslct_symlink_path.is_symlink() or exaslct_symlink_path.exists() or exaslct_symlink_path.is_file()

    if exaslct_symlin_exists and not force_install:
        print(f"The path for the symlink to exaslct at {exaslct_symlink_path} already exists.")
        print("Do you want to remove it and continue with installation?")
        answer = input("yes/no:")

        if answer == "yes":
            exaslct_symlink_path.unlink()
        else:
            print("Can't continue with the installation, because the path to exaslct symlink already exists.")
            print("You can change the path to exaslct symlink by setting the environment variable EXASLCT_SYM_LINK_PATH")
            sys.exit(1)
    elif force_install:
        exaslct_symlink_path.unlink()

    exaslct_symlink_path.symlink_to(target_script_path / "exaslct.sh")

