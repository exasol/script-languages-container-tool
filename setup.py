# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_script_languages_container_tool',
 'exasol_script_languages_container_tool.cli',
 'exasol_script_languages_container_tool.cli.commands',
 'exasol_script_languages_container_tool.cli.options',
 'exasol_script_languages_container_tool.lib',
 'exasol_script_languages_container_tool.lib.tasks',
 'exasol_script_languages_container_tool.lib.tasks.build',
 'exasol_script_languages_container_tool.lib.tasks.clean',
 'exasol_script_languages_container_tool.lib.tasks.export',
 'exasol_script_languages_container_tool.lib.tasks.push',
 'exasol_script_languages_container_tool.lib.tasks.save',
 'exasol_script_languages_container_tool.lib.tasks.test',
 'exasol_script_languages_container_tool.lib.tasks.upload',
 'exasol_script_languages_container_tool.lib.utils']

package_data = \
{'': ['*']}

install_requires = \
['exasol-integration-test-docker-environment @ '
 'git+https://github.com/exasol/integration-test-docker-environment.git@0.2.0']

setup_kwargs = {
    'name': 'exasol-script-languages-container-tool',
    'version': '0.2.0',
    'description': 'Script Languages Container Tool',
    'long_description': "# PostgreSQL Virtual Schema\n\n# Overview\n\nThe Script-Languages-Container-Tool (exaslct) is the build tool for the script language container.\nYou can build, export and upload script-language container from so called flavors \nwhich are description how to build the script language container. You can find pre-defined flavors \nin the [script-languages-release](https://github.com/exasol/script-languages-release) repository. \nThere we also described how you could customize these flavors to your needs.\n\n## In a Nutshell\n\n### Prerequisites\n\n#### For installation\n\nIn order to install this tool, your system needs to provide \nthe following prerequisites:\n\n* Software\n    * Linux\n    * [bash](https://www.gnu.org/software/bash/)\n    * [coreutils](https://www.gnu.org/software/coreutils/)\n      * sha512sum\n      * sed\n    * [curl](https://curl.se/)\n\n#### For running\n\nIn order to use this tool, your system needs to fulfill the followin prerequisites:\n\n* Software\n    * Linux\n    * [bash](https://www.gnu.org/software/bash/)\n    * [coreutils](https://www.gnu.org/software/coreutils/)\n      * readlink with -f option (the readlink version of MacOS doesn't support -f)\n      * dirname\n    * [Docker](https://docs.docker.com/) >= 17.05 \n      * with support for [multi-stage builds required](https://docs.docker.com/develop/develop-images/multistage-build/)\n      * host volume mounts need to be allowed\n    \n* System Setup  \n    * We recommend at least 50 GB free disk space on the partition \n      where Docker stores its images, on linux Docker typically stores \n      the images at /var/lib/docker.\n    * For the partition where the output directory (default: ./.build_output)\n      is located we recommend additionally at least 10 GB free disk space.\n\nFurther, prerequisites might be necessary for specific tasks. These are listed under the corresponding section.\n\n### Installation\n\nDownload the install and update script via:\n\n```\ncurl -L -o install_or_update_exaslct.sh https://raw.githubusercontent.com/exasol/script-languages-container-tool/main/installer/install_or_update_exaslct.sh\n```\n\nBefore you continue with installation, please compute with the following command \nthe sha512 hash sum of the downloaded file and compare it with its \n[checksum file](installer/checksums/install_or_update_exaslct.sh.sha512sum):\n\n```\nsha512sum install_or_update_exaslct.sh\n```\n\nIf the checksums are identical you can continue with the installation. \nPer default, the script installs exaslct into the current working directory.\nIt creates a script directory `exaslct_scripts` and the symlink `exaslct`\nto the starter script. If you want to change the path to the script directoy \nyou can set the environment variable EXASLCT_INSTALL_DIRECTORY and \nif you want to create the symlink somewhere else you can set $EXASLCT_SYM_LINK_PATH.  \n\n```\nbash install_or_update_exaslct.sh [version|git-commit-id|branch|tag] \n```\n\nYou can use the same script to change the version of your current installation.\nYou only need to provide a different version, git-commit-id, branch or tag. \n\n### Using exalsct\n\n#### How to build an existing flavor?\n\nCreate the language container and export it to the local file system\n\n```bash\n./exaslct export --flavor-path=flavors/<flavor-name> --export-path <export-path>\n```\n\nor upload it directly into the BuckerFS (currently http only, https follows soon)\n\n```bash\n./exaslct upload --flavor-path=flavors/<flavor-name> --database-host <hostname-or-ip> --bucketfs-port <port> \\ \n                   --bucketfs-username w --bucketfs-password <password>  --bucketfs-name <bucketfs-name> \\\n                   --bucket-name <bucket-name> --path-in-bucket <path/in/bucket>\n```\n\nOnce it is successfully uploaded, it will print the ALTER SESSION statement\nthat can be used to activate the script language container in the database.\n\n#### How to activate a script language container in the database\n\nIf you uploaded a container manually you can generate the language activation statement with\n\n```bash\n./exaslct generate-language-activation --flavor-path=flavors/<flavor-name> --bucketfs-name <bucketfs-name> \\\n                                         --bucket-name <bucket-name> --path-in-bucket <path/in/bucket> --container-name <container-name>\n```\n\nwhere \\<container-name> is the name of the uploaded archive without its file extension. To activate the language, execute the generated statement in your database session to activate the container for the current session or system wide.\n\nThis command will print a SQL statement to activate the language similiar to the following one:\n\n```bash\nALTER SESSION SET SCRIPT_LANGUAGES='<LANGUAGE_ALIAS>=localzmq+protobuf:///<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>?lang=<language>#buckets/<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>/exaudf/exaudfclient[_py3]';\n```\n\n**Please, refer to the User Guide for more detailed information, how to use exalsct.**\n\n## Features\n\n* Build a script language container as docker images\n* Export a script language container as an archive which can be used for extending Exasol UDFs\n* Upload a script language container as an archive to the Exasol DB's BucketFS\n* Generating the activation command for a script language container\n* Can use Docker registries, such as Docker Hub, as a cache to avoid rebuilding image without changes\n* Can push Docker images to Docker registries\n* Run tests for you container against a Exasol DB (docker-db or external db)\n\n## Table of Contents\n\n### Information for Users\n\n* [User Guide](doc/user_guide/user_guide.md)\n* [Changelog](doc/changes/changelog.md)\n\n## Information for Developers\n\n* [Developer Guide](doc/developer_guide/developer_guide.md)\n* [Design](doc/design.md)",
    'author': 'Torsten Kilias',
    'author_email': 'torsten.kilias@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exasol/script-languages-container-tool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
