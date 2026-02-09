#! /usr/bin/env python3

# The imports from `commands` are required so that `cli()` will print the available
# subcommands. Unfortunately, as these are unused imports within this file, an
# auto-formatting tool would want to remove them, so we added # noqa: F401.
import exasol.slc.tool.commands  # noqa: F401
from exasol.slc.tool.cli import cli


def main():
    cli()


if __name__ == "__main__":
    main()
