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
    'long_description': '',
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
