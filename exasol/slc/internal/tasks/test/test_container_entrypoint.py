#!/usr/bin/env python3
"""Entry point for executing tests inside the test container."""

import os
import subprocess
import sys

# TODO: Move to test container + uid/gid magic


def build_command(arguments: list[str]) -> list[str]:
    """Build the command for the configured test framework.

    The arguments after the entry-point script are intentionally passed through
    unchanged. This keeps the existing unittest command-line interface intact
    while allowing the same test container to run pytest tests.
    """
    if not arguments:
        raise ValueError("A test file and its arguments must be provided.")

    if os.environ.get("EXASLCT_EXECUTION_MODE", "unittest") == "pytest":
        return ["pytest", *arguments]
    return ["python3", *arguments]


def main() -> int:
    return subprocess.run(build_command(sys.argv[1:]), check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
