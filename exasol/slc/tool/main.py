#! /usr/bin/env python3

import multiprocessing
import sys

# The imports from `commands` are required so that `cli()` will print the available
# subcommands. Unfortunately, as these are unused imports within this file, an
# auto-formatting tool would want to remove them, so we added # noqa: F401.
import exasol.slc.tool.commands  # noqa: F401
from exasol.slc.tool.cli import cli


def main():
    # Python 3.14 changes the default multiprocessing start method on Linux to
    # forkserver, which breaks Luigi's parallel task execution (workers share
    # module-level state that forkserver/spawn workers don't inherit).
    if sys.platform == "linux":
        multiprocessing.set_start_method("fork", force=True)
    cli()


if __name__ == "__main__":
    main()
