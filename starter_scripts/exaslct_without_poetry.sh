#!/bin/bash

set -euo pipefail

[[ "$(uname)" = Darwin ]] && rl=greadlink || rl=readlink

if [[ ! "$(command -v $rl)" ]]; then
  echo readlink not available! Please install coreutils: On Linux \"apt-get install coreutils\" or similar. On MacOsX \"brew install coreutils\".
  exit 1
fi

SCRIPT_DIR="$(dirname "$($rl -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR="$SCRIPT_DIR/.."

export PYTHONPATH="$PROJECT_ROOT_DIR/"
python3 -u "$PROJECT_ROOT_DIR/exasol_script_languages_container_tool/main.py" "${@}" # We use "$@" to pass the commandline arguments to the run function to preserve arguments with spaces as a single argument
exit $?
