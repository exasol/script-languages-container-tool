#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR="$SCRIPT_DIR/.."

export PYTHONPATH="$PROJECT_ROOT_DIR/"
python3 "$PROJECT_ROOT_DIR/exasol_script_languages_container_tool/main.py" "${@}" # We use "$@" to pass the commandline arguments to the run function to preserve arguments with spaces as a single argument
exit $?
