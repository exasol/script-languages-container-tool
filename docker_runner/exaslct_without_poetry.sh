#!/bin/bash

set -euo pipefail

#####################################################################################
###REMEMBER TO TEST ANY CHANGES HERE ON MACOSX!!!
#####################################################################################


rl=readlink
if [[ "$(uname)" = Darwin ]]; then
  rl=greadlink
fi

if [[ ! "$(command -v $rl)" ]]; then
  echo readlink not available! Please install coreutils: On Linux \"apt-get install coreutils\" or similar. On MacOsX \"brew install coreutils\".
  exit 1
fi

SCRIPT_DIR="$(dirname "$($rl -f "${BASH_SOURCE[0]}")")"
PROJECT_ROOT_DIR="$SCRIPT_DIR/.."

#This script is supposed to run only within the docker runner. So we can assume that project is stored under /script-languages-container-tool !!!
python3 -u "/script-languages-container-tool/exasol_script_languages_container_tool/main.py" "${@}" # We use "$@" to pass the commandline arguments to the run function to preserve arguments with spaces as a single argument
exit $?
