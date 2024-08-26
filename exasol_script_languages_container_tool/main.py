#! /usr/bin/env python3

import exasol_integration_test_docker_environment.cli.commands
from exasol_integration_test_docker_environment.cli.cli import cli

import exasol_script_languages_container_tool.cli.commands


def main():
    cli()


if __name__ == "__main__":
    main()
