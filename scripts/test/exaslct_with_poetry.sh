#!/usr/bin/env bash


SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR=$"$SCRIPT_DIR/../.."

#shellcheck source=./scripts/build/poetry_utils.sh
source "$SCRIPT_DIR/../build/poetry_utils.sh"

check_requirements

set -euo pipefail

init_poetry

if [ -n "$POETRY_BIN" ]
then
  $POETRY_BIN run bash python3 -u "$PROJECT_ROOT_DIR/exasol_script_languages_container_tool/main.py" "${@}" # We use "$@" to pass the commandline arguments to the run function to preserve arguments with spaces as a single argument
else
  echo "Could not find poetry!"
  exit 1
fi
