#! /usr/bin/env python3

from exasol_integration_test_docker_environment.cli.cli import cli
import exasol_integration_test_docker_environment.cli.commands
import exasol_script_languages_container_tool.cli.commands


def main():
    cli()


if __name__ == '__main__':
    main()
