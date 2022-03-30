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
 'exasol_script_languages_container_tool.lib.tasks.install_starter_scripts',
 'exasol_script_languages_container_tool.lib.tasks.push',
 'exasol_script_languages_container_tool.lib.tasks.save',
 'exasol_script_languages_container_tool.lib.tasks.security_scan',
 'exasol_script_languages_container_tool.lib.tasks.test',
 'exasol_script_languages_container_tool.lib.tasks.upload',
 'exasol_script_languages_container_tool.lib.utils']

package_data = \
{'': ['*'], 'exasol_script_languages_container_tool': ['starter_scripts/*']}

install_requires = \
['exasol-integration-test-docker-environment @ '
 'https://github.com/exasol/integration-test-docker-environment/releases/download/0.9.0/exasol_integration_test_docker_environment-0.9.0-py3-none-any.whl',
 'importlib_metadata>=4.6.0']

setup_kwargs = {
    'name': 'exasol-script-languages-container-tool',
    'version': '0.10.0',
    'description': 'Script Languages Container Tool',
    'long_description': "# Script-Languages-Container-Tool\n\n## Overview\n\nThe Script-Languages-Container-Tool (exaslct) is the build tool for the script language container.\nYou can build, export and upload script-language container from so-called flavors \nwhich are description how to build the script language container. You can find pre-defined flavors \nin the [script-languages-release](https://github.com/exasol/script-languages-release) repository. \nThere we also described how you could customize these flavors to your needs.\n\n## In a Nutshell\n\n### Prerequisites\n\n#### For installation\n\nIn order to install this tool, your system needs to provide \nthe following prerequisites:\n\n* Software\n    * Linux\n      * [bash](https://www.gnu.org/software/bash/) >= 4.2\n    * MacOsX\n      * [bash](https://www.gnu.org/software/bash/) > 3.2\n    * [coreutils](https://www.gnu.org/software/coreutils/)\n      * sha512sum\n      * sed\n    * [curl](https://curl.se/)\n    * Python 3 (>=3.6)\n      * Pip\n\n\n#### For running\n\nIn order to use this tool, your system needs to fulfill the following prerequisites:\n\n* Software\n    * Linux\n      * [bash](https://www.gnu.org/software/bash/) >= 4.2\n      * [coreutils](https://www.gnu.org/software/coreutils/)\n        * readlink with -f option\n        * realpath  \n        * dirname\n    * MacOsX (Please see limitations on [MacOsX](#macosx-limitations))\n      * [bash](https://www.gnu.org/software/bash/) >= 3.2\n      * [coreutils](https://www.gnu.org/software/coreutils/)\n        * greadlink with -f option\n        * realpath  \n        * dirname\n    * [Docker](https://docs.docker.com/) >= 17.05 \n      * with support for [multi-stage builds required](https://docs.docker.com/develop/develop-images/multistage-build/)\n      * host volume mounts need to be allowed\n\n* System Setup  \n    * We recommend at least 50 GB free disk space on the partition \n      where Docker stores its images, on linux Docker typically stores \n      the images at /var/lib/docker.\n    * For the partition where the output directory (default: ./.build_output)\n      is located we recommend additionally at least 10 GB free disk space.\n\nFurther, prerequisites might be necessary for specific tasks. These are listed under the corresponding section.\n\n### Installation\n\nFind the wheel package for a specific [release](https://github.com/exasol/script-languages-container-tool/releases) under assets.\n\nInstall the python package with `python3 -m pip install https://github.com/exasol/script-languages-container-tool/releases/download/$VERSION/exasol_script_languages_container_tool-$VERSION-py3-none-any.whl`. Replace $VERSION with the latest version or the specific version you are interested in.\n\nThen you can use the Python package itself or install the starter scripts which allow to run exaslct within a docker image:\n`exasol_script_languages_container_tool.main install-starter-scripts --install-path $YOUR_INSTALL_PATH`\n\nThis will create a subfolder with the scripts itself and a symlink `exaslct` in $YOUR_INSTALL_PATH, which can be used as entry point.\n\n### Usage\n\n#### How to build an existing flavor?\n\nCreate the language container and export it to the local file system\n\n```bash\n./exaslct export --flavor-path=flavors/<flavor-name> --export-path <export-path>\n```\n\nor upload it directly into the BucketFS (currently http only, https follows soon)\n\n```bash\n./exaslct upload --flavor-path=flavors/<flavor-name> --database-host <hostname-or-ip> --bucketfs-port <port> \\ \n                   --bucketfs-username w --bucketfs-password <password>  --bucketfs-name <bucketfs-name> \\\n                   --bucket-name <bucket-name> --path-in-bucket <path/in/bucket>\n```\n\nOnce it is successfully uploaded, it will print the ALTER SESSION statement\nthat can be used to activate the script language container in the database.\n\n#### How to activate a script language container in the database\n\nIf you uploaded a container manually, you can generate the language activation statement with\n\n```bash\n./exaslct generate-language-activation --flavor-path=flavors/<flavor-name> --bucketfs-name <bucketfs-name> \\\n                                         --bucket-name <bucket-name> --path-in-bucket <path/in/bucket> --container-name <container-name>\n```\n\nwhere \\<container-name> is the name of the uploaded archive without its file extension. To activate the language, execute the generated statement in your database session to activate the container for the current session or system wide.\n\nThis command will print a SQL statement to activate the language similar to the following one:\n\n```bash\nALTER SESSION SET SCRIPT_LANGUAGES='<LANGUAGE_ALIAS>=localzmq+protobuf:///<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>?lang=<language>#buckets/<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>/exaudf/exaudfclient[_py3]';\n```\n\n**Please, refer to the User Guide for more detailed information, how to use exalsct.**\n\n## Features\n\n* Build a script language container as docker images\n* Export a script language container as an archive which can be used for extending Exasol UDFs\n* Upload a script language container as an archive to the Exasol DB's BucketFS\n* Generating the activation command for a script language container\n* Can use Docker registries, such as Docker Hub, as a cache to avoid rebuilding image without changes\n* Can push Docker images to Docker registries\n* Run tests for you container against an Exasol DB (docker-db or external db)\n\n## Limitations\n\n* Caution with symbolic links: \n  If you use symbolic links inside any directory of the command line arguments\n  they must not point to files or directories outside the root of the path of the \n  command line argument (i.e. --flavor-path ./flavors/my_flavor/ => There must be no symbolic\n  link inside ./flavors/my_flavor point to anywhere outside of ./flavors/my_flavor).\n  Background: Local directories paths must be mounted manually to the docker container. \n  We currently support only the mounting of the given command line arguments, but we do not analyze\n  the content of those directories.\n  Plan is to fix this limitation with [#35](https://github.com/exasol/script-languages-container-tool/issues/35)\n\n\n### MacOsX Limitations\n  \n* On MacOsX all arguments (flavors path, output directory, etc.) must point to locations within the current directory (background is that the MacOsX version does not support mount binding additional directories).\n\n## Table of Contents\n\n### Information for Users\n\n* [User Guide](doc/user_guide/user_guide.md)\n* [Changelog](doc/changes/changelog.md)\n\n## Information for Developers\n\n* [Developer Guide](doc/developer_guide/developer_guide.md)\n* [Dependencies](doc/dependencies.md)\n",
    'author': 'Torsten Kilias',
    'author_email': 'torsten.kilias@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exasol/script-languages-container-tool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
