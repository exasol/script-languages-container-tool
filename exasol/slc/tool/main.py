#! /usr/bin/env python3

import exasol_integration_test_docker_environment.cli.commands  # type: ignore
from exasol_integration_test_docker_environment.cli.cli import cli  # type: ignore

import exasol.slc.tool.commands


def main():
    cli()


if __name__ == "__main__":
    main()
